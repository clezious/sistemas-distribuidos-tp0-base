import socket
import logging


class Protocol:
    def __init__(self):
        pass

    @staticmethod
    def read_client_message(client_sock: socket.socket):
        msg = ""
        while (char := client_sock.recv(1).decode('utf-8')) != '\n':
            msg += char
        addr = client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
        return msg.split("|")

    @staticmethod
    def send_server_message(client_sock: socket.socket, msg):
        msg = "{}\n".format(msg).encode('utf-8')
        msg_len = len(msg)
        sent = 0
        while sent < msg_len:
            sent += client_sock.send(msg[sent:])
