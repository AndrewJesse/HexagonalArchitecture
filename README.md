# DesignPatternProject

Minimal ports-and-adapters example: one app port, one production plugin (SQLite),
and one test plugin (in-memory). The sample reads user input and writes it to the
database.

## Run

From the repository root:

```bash
python3 main.py
```

## Tests

Standard library only (`unittest`):

```bash
python3 -m unittest discover -s plugins/tests -v
```

## Architecture

This project uses ports and adapters (hexagonal-style) layering so the domain
stays independent of how data is stored or presented.

### Dependency direction

- `model/` - No imports from `app` or `plugins`. Pure types and functions.
- `app/` - Imports `model` and defines ports (`Protocol`s). Orchestrates use
  cases; does not import concrete adapters.
- `plugins/` - Implements ports (e.g. in-memory store, SQLite). May import
  `model` types for signatures.
- `plugins/tests/` - Exercises `app` and plugins without production I/O.

Outer layers depend on inner concepts; the center does not depend on frameworks
or storage details.

### Ports and adapters

- **Ports** - Abstract interfaces in `app/ports.py` (`PayloadWriter`).
  They describe what the application needs, not how it is done.
- **Adapters/Plugins** - Concrete implementations in `plugins/` that satisfy
  those protocols.

Wiring happens at the composition root (`main.py`): choose an adapter and pass
it into `persist_user_memo.write_user_input`.

### Why this shape

- Swap storage or integrations without rewriting core logic.
- Test use cases and domain rules with fakes or in-memory adapters.
- Give teams a clear map of where code belongs.

### How to add code and keep separation

1. New business rules or data shapes -> put them in `model/`. Do not import
   `app` or `plugins` from here.
2. New workflow -> add/extend functions in `app/` (e.g. `persist_user_memo.py`). Depend
   on `model` and port types from `app/ports.py`, not concrete stores.
3. New persistence or integration -> add module in `plugins/` implementing
   protocols in `app/ports.py`. Wire in `main.py`, not `model/`.
4. New external capability -> declare a `Protocol` in `app/ports.py`, use it
   from `app/persist_user_memo.py`, and implement it under `plugins/`.

Rule of thumb: dependencies flow inward - `model` depends on nothing in this
app; `app` depends on `model` and abstractions; `plugins` depends on `model`
and implements ports defined by `app`.

### Application flow

```mermaid
flowchart LR
    M[main.py<br/>composition root]
    A[InMemoryStore<br/>plugin in plugins/]
    P[app.persist_user_memo.write_user_input<br/>use case]

    M -->|inject as PayloadWriter| P
    P -->|write(payload)| A
```

## Folder guide

### `model/` - domain model and pure logic

**Purpose**

Holds types and functions that express business rules with no I/O:
no files, databases, network, UI, or hardware drivers.

**What belongs here**

- Dataclasses (or similar) for domain data, e.g. `Payload`.
- Simple value types used across layers.

**What does not belong here**

- Imports from `app`, `plugins`, or adapter/UI packages.
- Code that reads/writes disk, talks to external systems, or touches UI.

### `app/` - application layer (use cases and ports)

**Purpose**

Orchestrates what the system does: accept user input and persist results.
Defines ports as abstract interfaces.

**What belongs here**

- Use cases / pipelines: `persist_user_memo.write_user_input`.
- Ports in `ports.py` (`PayloadWriter`).
- Package entrypoint: `__main__.py` for `python3 main.py`.

**What does not belong here**

- Low-level I/O implementations (those live under `plugins/`).

### `plugins/` - adapters (infrastructure / persistence)

**Purpose**

Implements ports from `app/ports.py` with concrete mechanisms:
in-memory dicts, SQLite, files, REST clients, PLC gateways, etc.

**What belongs here**

- Classes that implement `PayloadWriter` (or future protocols).
- Thin mapping between port types (`Payload`) and SQL/bytes/HTTP/tag formats.

**In this repo**

- `memory.py` - `InMemoryStore` test plugin.
- `sqlite_store.py` - production SQLite plugin (migrations in `data/sql/`).

### `plugins/tests/` - automated tests

**Purpose**

Verifies `app` behavior without requiring real hardware, production databases,
or manual steps.

**Conventions**

- Uses standard library `unittest`.
- Run from repo root:

  ```bash
  python3 -m unittest discover -s plugins/tests -v
  ```

## Refactoring existing code (quick guide)

When refactoring, keep behavior the same and move one boundary at a time.

1. Start at the app boundary (`app/persist_user_memo.py`) and keep port signatures stable.
2. Move/rename internals in small steps, then run tests.
3. If storage details leak into `app/`, move them back into `plugins/`.
4. Add one focused test before or during the refactor for the behavior you are preserving.

Example: extract payload creation into a helper without changing behavior.

```python
# app/persist_user_memo.py
from datetime import datetime

from .ports import PayloadWriter
from model.transform import Payload


def _build_payload(user_text: str) -> Payload:
    return Payload(
        text=user_text.strip(),
        date=datetime.now().isoformat(timespec="seconds"),
    )


def write_user_input(writer: PayloadWriter, user_text: str) -> Payload:
    payload = _build_payload(user_text)
    writer.write(payload)
    return payload
```

## Adding new functionality (with example)

Pattern to add a feature:

1. Add/update domain type(s) in `model/` if needed.
2. Add a new app use case in `app/persist_user_memo.py`.
3. Reuse existing port if possible, otherwise add a new port in `app/ports.py`.
4. Implement the new behavior in one or more plugins.
5. Wire it in `main.py` and add a test in `plugins/tests/`.

Example: add `write_greeting_input` that prefixes text.

```python
# app/persist_user_memo.py
def write_greeting_input(writer: PayloadWriter, name: str) -> Payload:
    payload = Payload(
        text=f"Hello, {name.strip()}!",
        date=datetime.now().isoformat(timespec="seconds"),
    )
    writer.write(payload)
    return payload
```

```python
# plugins/tests/test_write_user_input.py
def test_writes_greeting_text(self) -> None:
    store = InMemoryStore()
    saved = write_greeting_input(store, "  Andrew  ")
    self.assertEqual(saved.text, "Hello, Andrew!")
```
