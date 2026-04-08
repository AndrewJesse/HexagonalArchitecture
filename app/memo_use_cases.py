from datetime import datetime

from .ports import PayloadWriter
from model.transform import Payload


def write_user_input(writer: PayloadWriter, user_text: str) -> Payload:
    payload = Payload(
        text=user_text.strip(),
        date=datetime.now().isoformat(timespec="seconds"),
    )
    writer.write(payload)
    return payload
