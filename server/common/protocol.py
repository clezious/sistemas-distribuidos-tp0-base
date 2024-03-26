import socket
import logging


class Protocol:
    def __init__(self):
        pass

    @staticmethod
    def _read_line(client_sock: socket.socket) -> str:
        msg = ""
        while (char := client_sock.recv(1).decode('latin-1')) != '\n':
            msg += char
        return msg

    @staticmethod
    def read_client_message(client_sock: socket.socket):
        msg = Protocol._read_line(client_sock)
        if msg == "BATCH_START":
            bets = []
            while (msg := Protocol._read_line(client_sock)) != "BATCH_END":
                bets.append(msg.split(","))
            return {'action': 'batch', 'data': {'bets': bets}}
        elif msg.startswith("FINISHED"):
            return {'action': 'client_finished', 'data': {"agency": msg.split(",")[1]}}
        elif msg.startswith("QUERY"):
            return {'action': 'query', 'data': {"agency": msg.split(",")[1]}}
        addr = client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
        return {'action': 'bet', 'data': msg.split(",")}

    @staticmethod
    def send_server_message(client_sock: socket.socket, action: str, data: dict = None):
        msg = Protocol.generate_message_content(action, data)
        msg = '{}\n'.format(msg).encode('latin-1')
        msg_len = len(msg)
        sent = 0
        while sent < msg_len:
            sent += client_sock.send(msg[sent:])

    @staticmethod
    def generate_message_content(action: str, data: dict = None) -> str:
        if action == 'query':
            return 'QUERY_FAIL' if data.get('result') == 'fail' else f'QUERY_SUCCESS,{data.get("winners")}'
        return f"{action.upper()}"
