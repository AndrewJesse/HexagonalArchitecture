# Composition Root (aka "main" or "bootstrap").
#
# This is the ONLY place in the entire project that knows about BOTH
# concrete adapters — the driven adapter (SqliteStore for persistence)
# and the driving adapter (cli for user interaction).
#
# It wires them together through the port (PayloadWriter protocol).
#
# In Ports & Adapters, the composition root sits OUTSIDE the hexagon.
# It is not part of domain, application, or adapter layers — it just
# assembles them together.
from adapters.driven.sqlite_store import SqliteStore
from adapters.driving.cli import run as run_cli


def main() -> None:
    store = SqliteStore("data/data.db")   # driven adapter (right side)
    run_cli(store)                         # driving adapter (left side)


if __name__ == "__main__":
    main()
