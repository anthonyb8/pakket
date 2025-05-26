from ..transmission.server import TcpServer, TransmissionServer, UdpServer


class Handler:
    def __init__(self, transmission: TransmissionServer) -> None:
        self.transmission = transmission


if __name__ == "__main__":
    transmission = TcpServer("127.0.0.1", 1234)
    server = ProtocolServer(transmission)
