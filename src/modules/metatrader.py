import json

import backoff
import zmq

from src.settings import settings


class SocketConnectionError(Exception):
    pass


@backoff.on_exception(
    backoff.expo,
    SocketConnectionError,
    max_tries=settings.MAX_TRIES,
)
def recieve_msg(socket):
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    socks = dict(poller.poll(settings.SOCKET_TIMEOUT))
    if socks:
        if socks.get(socket) == zmq.POLLIN:
            message = socket.recv(zmq.NOBLOCK)
            message = json.loads(message.decode("utf-8").replace("'",'"').replace('True', 'true').replace('False', 'false'))
            return message
    else:
        raise SocketConnectionError


def request_mt(service_name: str, text: str):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{service_name}")
    socket.send(text.encode(encoding='UTF-8'))
    message = recieve_msg(socket)
    socket.close()
    return message
