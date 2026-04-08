from typing import Protocol

from logic.transform import Payload


class DataSource(Protocol):
    def read(self) -> Payload: ...


class DataSink(Protocol):
    def write(self, data: Payload) -> None: ...
