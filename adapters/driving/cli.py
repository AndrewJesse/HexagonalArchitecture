# Adapter — Driving (primary) CLI adapter.
#
# A driving adapter sits on the LEFT side of the hexagon: it receives
# user input and DRIVES the application through its use-case API.
#
# This adapter knows about the application layer (use cases) but the
# application layer never knows about this adapter.
from application.services import write_user_input
from application.ports import PayloadWriter


def run(writer: PayloadWriter) -> None:
    user_text = input("Enter text: ")
    result = write_user_input(writer, user_text)
    print(f"Saved: {result}")
