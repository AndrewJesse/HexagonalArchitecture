from dataclasses import asdict

from model.transform import Payload


class InMemoryStore:
    def __init__(self) -> None:
        self._data: dict = {}

    def write(self, data: Payload) -> None:
        self._data.clear()
        self._data.update(asdict(data))

    def last(self) -> Payload:
        if not self._data:
            return Payload()
        return Payload(
            text=str(self._data.get("text", "") or ""),
            date=self._data.get("date"),
        )
