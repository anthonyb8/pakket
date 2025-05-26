from abc import ABC, abstractmethod
import socket
import time
from typing import Union
from pool import TcpTask, ThreadPool, Task, UdpTask
import threading

HOST = "127.0.0.1"
PORT = 1234


class Listener(ABC):
    @abstractmethod
    def listen(self):
        pass


class UdpListener(Listener):
    def __init__(self, host: str, port: int, threads: int = 10):
        self.host = host
        self.port = port
        self.protocol = socket.SOCK_DGRAM
        self.ip_family = socket.AF_INET
        self.socket = socket.socket(self.ip_family, self.protocol)
        self.socket.bind((HOST, PORT))
        self.socket.settimeout(1.0)

        # self.shutdown_event = threading.Event()
        # self.pool = ThreadPool(threads)
        # self.conn_thread = threading.Thread(target=self.connect)
        # self.conn_thread.start()

    def listen(self) -> Union[Task, None]:
        # while not self.shutdown_event.is_set():
        try:
            msg = self.socket.recvfrom(1024)
            task = UdpTask(self.socket, msg[0], msg[1][0], msg[1][1])
            return task
            # self.pool.add(task)
        except socket.timeout:
            return None
        except Exception as e:
            return Exception(f"Unexpected recieve error : {e}")

    #
    # def close(self):
    #     self.shutdown_event.set()
    #     self.pool.close()
    #     self.conn_thread.join()


class TcpListener(Listener):
    def __init__(self, host: str, port: int, threads: int = 10):
        self.host = host
        self.port = port
        self.protocol = socket.SOCK_STREAM
        self.ip_family = socket.AF_INET
        self.socket = socket.socket(self.ip_family, self.protocol)
        self.socket.bind((HOST, PORT))
        self.socket.listen(100)
        self.socket.settimeout(1.0)

        # self.shutdown_event = threading.Event()
        # self.pool = ThreadPool(threads)
        # self.conn_thread = threading.Thread(target=self.connect)
        # self.conn_thread.start()

    def listen(self):
        # while not self.shutdown_event.is_set():
        try:
            conn, addr = self.socket.accept()
            return TcpTask(conn, addr[0], addr[1])
            # self.pool.add(task)
        except socket.timeout:
            return
        except Exception as e:
            return Exception(f"Unexpected recieve error : {e}")

    # def close(self) -> None:
    #     self.shutdown_event.set()
    #     self.pool.close()
    #     self.conn_thread.join()


if __name__ == "__main__":
    server = TcpListener(HOST, PORT)
    # server = UdpListener(HOST, PORT)

    time.sleep(10)
    server.close()
