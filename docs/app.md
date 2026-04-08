# `app/` — application layer (use cases and ports)

## Purpose

Orchestrates **what the system does**: load data, call domain logic, persist results. Also defines **ports** — abstract interfaces (`Protocol`s) that describe what the app needs from the outside world without naming a concrete database, file, or device.

## What belongs here

- **Use cases / pipelines** — e.g. `pipeline.run`: coordinate `DataSource`, domain functions, and `DataSink`.
- **Ports** — `Protocol` definitions in `ports.py` (e.g. `DataSource`, `DataSink`).
- **Package entrypoint** — `__main__.py` supports `python -m app` and delegates to the root composition.

## What does not belong here

- Low-level I/O implementations (those live under **`data/`** or future adapter packages).
- UI widgets or framework-specific screen code (future **`presentation/`** / **`ui`** layer would call into `app`, not live inside domain rules).

## Dependencies

- **May import** `model` and declare types used in ports.
- **Must not** import concrete classes from `data` inside `pipeline.py` — only the port types, so implementations stay swappable.

## In this repo

- `ports.py` — `DataSource`, `DataSink`.
- `pipeline.py` — `run` use case.
- `__main__.py` — entry when using `python -m app`.
