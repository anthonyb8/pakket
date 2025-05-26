from .listener.server import Listener, TcpListener
from .listener.pool import TcpTask, ThreadPool, Task, UdpTask

# from .application.server import *
from abc import ABC, abstractmethod
import queue
import threading


class Handler(ABC):
    @abstractmethod
    def handle(self):
        pass


class HttpHandler:
    def handle(self):
        pass


class Service:
    def __init__(
        self,
        listener: Listener,
        handler: Handler,
        threads: int = 10,
    ):
        self.listener = listener
        self.handler = handler
        self.task_queue: queue.Queue[Task | None] = queue.Queue()
        self.threads = [
            threading.Thread(target=self.worker_thread) for _ in range(0, 10)
        ]

        self.shutdown_event = threading.Event()
        self.pool = ThreadPool(threads)
        self.conn_thread = threading.Thread(target=self.connect)
        self.conn_thread.start()
        for t in self.threads:
            t.start()

    def connect(self):
        while not self.shutdown_event.is_set():
            try:
                task = self.listener.listen()

                if task:
                    self.pool.add(task)
            except Exception as e:
                return Exception(e)

            # self.pool.add(self.listener.listen())

    def handle(self):
        while not self.shutdown_event.is_set():
            self.handler.handle()

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


if __name__ == "__main__":
    listener = TcpListener("127.0.0.1", 1234)
    handler = Handler()
    service = Service(listener, handler)
