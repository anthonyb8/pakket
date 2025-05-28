import time
from server import (
    Http,
    HttpResponse,
    StatusCode,
    TcpListener,
    SocketAddr,
    IpAddr,
)

http = Http()


@http.get("/hello")
def get_hello():
    return "Hello"


@http.post("/hello/{id}")
def post_hello(id: int, color: str, weight: float) -> HttpResponse:
    print(type(id))
    print(type(color))
    print(type(weight))
    print(f"ID:{id}")
    body = "Hello, World!".encode("utf-8")
    return HttpResponse(
        statuscode=StatusCode.OK,
        headers={"Content-Type": "text/plain"},
        body=body,
    )


@http.update("/hello")
def update_hello():
    return "Update Hello"


@http.delete("/hello")
def delete_hello():
    return "Delete Hello"


if __name__ == "__main__":
    addr = SocketAddr(IpAddr.V4, "127.0.0.1", 1234)
    tcp_server = TcpListener(addr, http)
    # udp_server = UdpListener(addr, http)

    # time.sleep(10)
    # tcp_server.close()
