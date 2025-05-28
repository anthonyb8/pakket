from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Message(ABC):
    @abstractmethod
    def to_bytes(self) -> bytes:
        raise NotImplementedError("Subclasses must implement this method")


class Service(ABC):
    @abstractmethod
    def call(self, msg: bytes) -> Message:
        pass
