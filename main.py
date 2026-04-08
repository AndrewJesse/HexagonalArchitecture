from app.pipeline import write_user_input
from plugins.sqlite_store import SqliteStore


def main() -> None:
    store = SqliteStore("data/data.db")
    user_text = input("Enter text: ")
    result = write_user_input(store, user_text)
    print(f"Saved: {result}")


if __name__ == "__main__":
    main()
