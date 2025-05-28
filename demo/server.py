from typing import Dict, List, Optional
from pydantic import BaseModel
from pakket.server import (
    Router,
    HttpResponse,
    StatusCode,
    TcpListener,
    SocketAddr,
    IpAddr,
)

router = Router()


class DemoModel(BaseModel):
    id: int
    name: str
    other: List[str]
    otherstuff: Dict[str, int]
    temp: Optional[int]


@router.get("/demo/{item_id}")
def get_demo(item_id: int) -> HttpResponse:
    if item_id == 1:
        return HttpResponse.ok("You got ID :1 ", StatusCode.OK)
    else:
        return HttpResponse.error("Invalid ID", StatusCode.BAD_REQUEST)


@router.post("/demo")
def post_demo(model: DemoModel) -> HttpResponse:
    try:
        s = f"You created instance id: {model.id}, name: {model.name},\
other: {model.other}, otherstuff: {model.otherstuff}, temp: {model.temp}"

        return HttpResponse.ok(s, StatusCode.OK)
    except Exception as e:
        return HttpResponse.error(str(e), StatusCode.BAD_REQUEST)


@router.put("/demo/{id}")
def update_demo(id: int, model: DemoModel):
    try:
        s = f"You Updated instance id: {id}, id: {model.id}, name: {model.name},\
other: {model.other}, otherstuff: {model.otherstuff}, temp: {model.temp}"
        return HttpResponse.ok(s, StatusCode.OK)
    except Exception as e:
        return HttpResponse.error(str(e), StatusCode.BAD_REQUEST)


@router.delete("/demo/{item_id}")
def delete_demo(item_id: int):
    if item_id == 1:
        return HttpResponse.ok("You deleted ID :1 ", StatusCode.OK)
    else:
        return HttpResponse.error("Invalid ID", StatusCode.BAD_REQUEST)


if __name__ == "__main__":
    addr = SocketAddr(IpAddr.V4, "127.0.0.1", 1234)
    tcp_server = TcpListener(addr, router)
