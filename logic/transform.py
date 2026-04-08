from dataclasses import dataclass


@dataclass
class Payload:
    text: str = ""
    count: int | None = None


def normalize(payload: Payload) -> Payload:
    text = payload.text.strip()
    return Payload(text=text, count=len(text))
