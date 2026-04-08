"""Run from repo root: python main.py  (same as: python -m app)."""

from app.pipeline import run
from data.memory import InMemoryStore
from model.transform import Payload


def main() -> None:
    store = InMemoryStore()
    store.write(Payload(text="  hello  "))
    result = run(store, store)
    print(result)


if __name__ == "__main__":
    main()
