import socket
import logging
from common.protocol import Protocol
from common.utils import Bet, store_bets, load_bets, has_won


class Server:
    def __init__(self, port, listen_backlog, total_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.should_stop = False
        self.clients_finished = set()
        self.total_clients = int(total_clients)

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

        while self.should_stop is False:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError:
                # Socket closed from outside
                continue

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
                store_bets(bets)
                logging.info(f'action: apuestas_almacenadas | result: success | batch_size: {len(bets)}')
                Protocol.send_server_message(client_sock, 'action: batch_processed | result: success')
            if msg['action'] == 'client_finished':
                self.clients_finished.add(msg['data']['agency'])
                logging.info(f'action: client_finished | result: success | clients_finished: {self.clients_finished}')
                if self.all_clients_finished():
                    logging.info('action: sorteo | result: success')
            if msg['action'] == 'query':
                if not self.all_clients_finished():
                    logging.info('action: query | result: fail')
                    Protocol.send_server_message(client_sock, 'QUERY_FAIL')
                else:
                    bets = load_bets()
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

    def all_clients_finished(self):
        return len(self.clients_finished) == self.total_clients
