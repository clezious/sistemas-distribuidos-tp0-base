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
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
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
            if msg['action'] == 'batch':
                bets = [Bet(*bet) for bet in msg['data']]
                self._store_bets(bets)
                logging.info(f'action: apuestas_almacenadas | result: success | batch_size: {len(bets)}')
                Protocol.send_server_message(client_sock, 'action: batch_processed | result: success')
            if msg['action'] == 'client_finished':
                self._add_client_finished(msg['data']['agency'])
                logging.info(f'action: client_finished | result: success | clients_finished: {self._get_clients_finished_count()}')
                if self.all_clients_finished():
                    logging.info('action: sorteo | result: success')
            if msg['action'] == 'query':
                if not self.all_clients_finished():
                    logging.info('action: query | result: fail')
                    Protocol.send_server_message(client_sock, 'QUERY_FAIL')
                else:
                    bets = self._load_bets()
                    agency = msg['data']['agency']
                    winners = len([bet for bet in bets if (bet.agency == int(agency) and has_won(bet))])
                    logging.info(f'action: query | result: success | agency: {agency} | winners: {winners}')
                    Protocol.send_server_message(client_sock, f'QUERY_SUCCESS,{winners}')

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
