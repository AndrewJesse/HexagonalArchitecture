from typing import Protocol

from model.transform import Payload


class PayloadWriter(Protocol):
    def write(self, data: Payload) -> None: ...
