import socket
import logging
from common.protocol import Protocol
from common.utils import Bet, store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.should_stop = False

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
            [agency, first_name, last_name, document, birthdate, number] = Protocol.read_client_message(client_sock)
            bet = Bet(agency, first_name, last_name, document, birthdate, number)
            store_bets([bet])
            response = f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}'
            logging.info(response)
            Protocol.send_server_message(client_sock, response)
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
