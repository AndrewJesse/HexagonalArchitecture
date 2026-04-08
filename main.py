from application.pipeline import run
from logic.transform import Payload
from persistence.memory import InMemoryStore


def main() -> None:
    store = InMemoryStore()
    store.write(Payload(text="  hello  "))
    result = run(store, store)
    print(result)


if __name__ == "__main__":
    main()
