import socket
import time
import threading


HOST = "127.0.0.1"
PORT = 1234


class TcpClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

    def connect(self):
        i = 0
        while i < 10:
            self.socket.sendall(b"This is the client")
            data = self.socket.recv(1024)

            print("Recieved", repr(data))
            i += 1

        self.socket.close()

    def close(self):
        pass


class UdpClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)

        self.shutdown_event = threading.Event()
        self.recieve_thread = threading.Thread(target=self.recieve)
        self.recieve_thread.start()

    def connect(self):
        self.socket.sendto("hello".encode(), (self.host, self.port))

    def recieve(self):
        while not self.shutdown_event.is_set():
            try:
                msg = self.socket.recvfrom(1024)
                print(msg)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Recieve error : {e}")

    def close(self):
        self.shutdown_event.set()
        self.recieve_thread.join()
        self.socket.close()


if __name__ == "__main__":
    client = TcpClient(HOST, PORT)
    client.connect()

    # client.connect()

    time.sleep(10)
    client.close()
