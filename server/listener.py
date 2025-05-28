import queue
import threading
import socket
from enum import Enum
from dataclasses import dataclass, field
from .base import Service, Message


class IpAddr(Enum):
    V4 = "V4"
    V6 = "V6"


@dataclass
class SocketAddr:
    addr_type: IpAddr
    host: str
    port: int
    ip_family: socket.AddressFamily = field(init=False)

    def __post_init__(self):
        match self.addr_type:
            case IpAddr.V4:
                self.ip_family = socket.AF_INET
            case IpAddr.V6:
                self.ip_family = socket.AF_INET6


@dataclass
class TransportMessage:
    socket: socket.socket
    addr: str
    port: int
    msg: bytes


class TcpListener(Service):
    def __init__(
        self,
        socket_addr: SocketAddr,
        service: Service,
        threads: int = 10,
    ):
        self.service = service
        self.socket_addr = socket_addr
        self.socket = socket.socket(socket_addr.ip_family, socket.SOCK_STREAM)
        self.socket.bind((socket_addr.host, socket_addr.port))
        self.socket.listen(100)
        self.socket.settimeout(1.0)

        # Thread Pool
        self.shutdown_event = threading.Event()
        self.task_queue = queue.Queue()
        self.threads = [
            threading.Thread(target=self.worker) for _ in range(threads)
        ]
        for t in self.threads:
            t.start()

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def listen(self):
        """Main thread receives messages and puts them into the task queue."""
        while not self.shutdown_event.is_set():
            try:
                conn, addr = self.socket.accept()
                msg = conn.recv(1024)
                request = TransportMessage(conn, addr[0], addr[1], msg)
                self.task_queue.put(request)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Unexpected receive error: {e}")

    def worker(self):
        """Worker thread pulls from queue and calls the inner service."""
        while not self.shutdown_event.is_set():
            try:
                request = self.task_queue.get(timeout=1)
                msg = self.call(request.msg)
                print(msg.to_bytes())
                request.socket.sendall(msg.to_bytes())
                request.socket.close()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    def call(self, msg: bytes) -> Message:
        return self.service.call(msg)

    def close(self):
        """Gracefully shutdown threads."""
        self.shutdown_event.set()
        self.listen_thread.join()

        for t in self.threads:
            t.join()


class UdpListener(Service):
    def __init__(
        self,
        socket_addr: SocketAddr,
        service: Service,
        threads: int = 10,
    ):
        self.service = service
        self.socket_addr = socket_addr
        self.socket = socket.socket(socket_addr.ip_family, socket.SOCK_DGRAM)
        self.socket.bind((socket_addr.host, socket_addr.port))
        self.socket.settimeout(1.0)

        self.shutdown_event = threading.Event()
        self.task_queue = queue.Queue()
        self.threads = [
            threading.Thread(target=self.worker) for _ in range(threads)
        ]
        for t in self.threads:
            t.start()

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def listen(self):
        """Main thread receives messages and puts them into the task queue."""
        while not self.shutdown_event.is_set():
            try:
                msg, addr = self.socket.recvfrom(1024)
                request = TransportMessage(self.socket, addr[0], addr[1], msg)
                self.task_queue.put(request)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Unexpected receive error: {e}")

    def worker(self):
        """Worker thread pulls from queue and calls the inner service."""
        while not self.shutdown_event.is_set():
            try:
                request = self.task_queue.get(timeout=1)
                response = self.call(request)

                self.socket.sendto(
                    response.to_bytes(),
                    (request.addr, request.port),
                )
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    def call(self, msg: bytes) -> Message:
        return self.service.call(msg)

    def close(self):
        """Gracefully shutdown threads."""
        self.shutdown_event.set()
        self.listen_thread.join()

        for t in self.threads:
            t.join()
