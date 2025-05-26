from abc import ABC, abstractmethod
import queue
import threading
import socket


class Task(ABC):
    @abstractmethod
    def run(self):
        pass


class UdpTask(Task):
    def __init__(
        self,
        socket: socket.socket,
        msg: bytes,
        addr: str,
        port: int,
    ):
        self.msg = msg
        self.addr = addr
        self.port = port
        self.socket = socket

    def run(self):
        print(self.msg.decode())
        self.socket.sendto("hello".encode(), (self.addr, self.port))


class TcpTask(Task):
    def __init__(self, conn: socket.socket, addr: str, port: int):
        self.conn = conn
        self.addr = addr
        self.port = port

    def run(self):
        print("running ")
        try:
            while True:
                data = self.conn.recv(1024)
                print(data)
                if data == b"":
                    print("closing connection")
                    break

                print(data)
                self.conn.sendall(b"This is the server")
        except BrokenPipeError:
            print("Broken pipe")
        except Exception as e:
            print(f"Error {e}")


class ThreadPool:
    def __init__(self, count: int) -> None:
        self.task_queue: queue.Queue[Task | None] = queue.Queue()
        self.threads = [
            threading.Thread(target=self.worker_thread)
            for _ in range(0, count)
        ]

        for t in self.threads:
            t.start()

    def add(self, task: Task) -> None:
        self.task_queue.put(task)

    def worker_thread(self) -> None:
        while True:
            task = self.task_queue.get()

            if task is None:
                break

            task.run()

    def close(self) -> None:
        for _ in self.threads:
            self.task_queue.put(None)

        for t in self.threads:
            t.join()
