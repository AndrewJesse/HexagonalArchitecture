# Architecture — ports and adapters

This project uses **ports and adapters** (hexagonal-style) layering so the **domain** stays independent of how data is stored or presented.

## Dependency direction

- **`model/`** — No imports from `app` or `data`. Pure types and functions.
- **`app/`** — Imports `model` and defines **ports** (`Protocol`s). Orchestrates use cases; does not import concrete adapters.
- **`data/`** — Implements ports (e.g. in-memory store). May import `model` types for signatures.
- **`test/`** — Exercises `model` and `app` (and adapters as needed) without production I/O.

Outer layers depend on inner concepts; the center does not depend on frameworks or storage details.

## Ports and adapters

- **Ports** — Abstract interfaces in `app/ports.py` (`DataSource`, `DataSink`). They describe *what* the application needs, not *how* it is done.
- **Adapters** — Concrete implementations in `data/` (and later UI, APIs, PLC drivers) that satisfy those protocols.

Wiring happens at the **composition root** (`main.py`): choose an adapter and pass it into `pipeline.run`.

## Why this shape

- Swap storage or integrations without rewriting core logic.
- Test use cases and domain rules with fakes or in-memory adapters.
- Give large teams a **shared map** of where code belongs (see per-folder notes in the repo).

## How to add code and keep separation

1. **New business rules or data shapes** — Put them in **`model/`**. Do **not** import `app` or `data` from here.

2. **New workflow (“do X then Y”)** — Add or extend functions in **`app/`** (e.g. `pipeline.py`). Depend on **`model`** and on **port** types from `app/ports.py`, not on concrete stores.

3. **New way to persist or read data** — Add a module under **`data/`** whose classes implement the **`Protocol`s** in `app/ports.py`. Wire implementations in **`main.py`** (or another composition root), not inside `model/`.

4. **New external capability** — Declare a **`Protocol`** in `app/ports.py`, use it from `app/pipeline.py`, and provide an implementation under **`data/`**.

5. **UI or HTTP later** — Treat them as adapters: they call into `app.pipeline` and map requests to domain types. Keep **`model`** free of UI/framework imports.

**Rule of thumb:** dependencies flow **inward** — `model` depends on nothing in this app; `app` depends on `model` and abstractions; `data` depends on `model` and implements ports defined by `app`.

## Benefits

- **Testability** — Pure logic in `model` and orchestration in `app` are easy to unit test without a database or filesystem.
- **Replaceable infrastructure** — Swap in-memory storage for files or a DB by adding an adapter and changing wiring in one place (`main.py`).
- **Clear boundaries** — Each folder has one kind of responsibility.
- **Safer refactors** — If ports stay stable, you can change storage or add APIs without rewriting core rules.
- **Technology isolation** — Domain rules do not depend on how data is stored or presented.
- **Documentation by structure** — Contributors can infer where code belongs from the folder names and rules above.

## Application flow (small)

```mermaid
flowchart LR
    M[main.py<br/>composition root]
    A[InMemoryStore<br/>adapter in data/]
    P[app.pipeline.run<br/>use case]
    D[model.normalize<br/>domain logic]

    M -->|inject as DataSource/DataSink| P
    A -->|read()| P
    P -->|normalize(payload)| D
    D -->|Payload| P
    P -->|write(payload)| A
```
