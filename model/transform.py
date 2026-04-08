from dataclasses import dataclass


@dataclass
class Payload:
    text: str = ""
    date: str | None = None
