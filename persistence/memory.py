from dataclasses import asdict

from logic.transform import Payload


class InMemoryStore:
    def __init__(self) -> None:
        self._data: dict = {}

    def read(self) -> Payload:
        if not self._data:
            return Payload()
        return Payload(
            text=str(self._data.get("text", "") or ""),
            count=self._data.get("count"),
        )

    def write(self, data: Payload) -> None:
        self._data.clear()
        self._data.update(asdict(data))
