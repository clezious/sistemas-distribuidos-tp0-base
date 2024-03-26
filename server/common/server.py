import socket
import logging
from common.protocol import Protocol
from common.utils import Bet, store_bets, load_bets, has_won
from multiprocessing import Process, Lock, Queue


class Server:
    def __init__(self, port, listen_backlog, total_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.should_stop = False
        self.clients_finished = Queue()
        self.total_clients = int(total_clients)
        self.lock = Lock()

    def stop(self):
        logging.debug("Gracefully stopping server")
        self.should_stop = True
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.debug("Server socket closed")

    def run(self):
        """
        Server loop

        Server that accepts a new connections and establishes a
        communication with a client. 
        Client interaction is then handled in a new process so that the server 
        can accept new connections and handle them in parallel.
        """
        processes = []
        while self.should_stop is False:
            try:
                client_sock = self.__accept_new_connection()
                p = Process(target=self.__handle_client_connection, args=(client_sock,))
                processes.append(p)
                p.start()
            except OSError:
                # Socket closed from outside
                continue
        for p in processes:
            p.join()

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = Protocol.read_client_message(client_sock)
            self._handle_client_message(client_sock, msg)
        except OSError as e:
            logging.error(f"action: handle_client_connection | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def _add_client_finished(self, agency):
        self.clients_finished.put(agency)

    def _get_clients_finished_count(self):
        return self.clients_finished.qsize()

    def all_clients_finished(self):
        return self._get_clients_finished_count() == self.total_clients

    def _store_bets(self, bets):
        self.lock.acquire()
        store_bets(bets)
        self.lock.release()

    def _load_bets(self):
        self.lock.acquire()
        bets = load_bets()
        self.lock.release()
        return bets

    def _handle_client_message(self, client_sock, msg):
        action: str = msg.get('action')
        data: dict = msg.get('data')
        if action == 'batch':
            bets = [Bet(*bet) for bet in data.get('bets')]
            self._store_bets(bets)
            logging.info(f'action: apuestas_almacenadas | result: success | batch_size: {len(bets)}')
            Protocol.send_server_message(client_sock, action='batch_processed', data={'result': 'success'})
        if action == 'client_finished':
            self._add_client_finished(data.get('agency'))
            logging.info(f'action: client_finished | result: success | clients_finished: {self._get_clients_finished_count()}')
            if self.all_clients_finished():
                logging.info('action: sorteo | result: success')
        if action == 'query':
            if not self.all_clients_finished():
                logging.info('action: query | result: fail')
                Protocol.send_server_message(client_sock, action='query', data={'result': 'fail'})
            else:
                bets = self._load_bets()
                agency = data.get('agency')
                winners = len([bet for bet in bets if (bet.agency == int(agency) and has_won(bet))])
                logging.info(f'action: query | result: success | agency: {agency} | winners: {winners}')
                Protocol.send_server_message(client_sock, action='query', data={'result': 'success', 'winners': winners})
