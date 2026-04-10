# Interview Questions — Hexagonal Architecture for HMI

Likely questions a hiring manager or technical lead would ask about this
project, with concise answers grounded in Cockburn's original article and
Clean Architecture principles.

---

## Architecture Fundamentals

### Q: Why hexagonal instead of a traditional layered architecture?

Layered architectures (UI → Business Logic → Database) create a top-to-bottom
dependency chain. Business logic leaks into the UI layer, and database details
leak into business logic — making both hard to test and hard to swap.

Hexagonal removes the top/bottom bias. There is only **inside** (business logic)
and **outside** (everything else). Every external concern — UI, database, CAN
bus, test harness — plugs in through the same kind of boundary (a port). This
means the application can be driven by a test script just as easily as by a
Qt GUI, and the database can be swapped without touching any business logic.

### Q: What is a port? What is an adapter?

A **port** is an interface that defines a conversation the application wants to
have. Example: `SignalWriter` says "I need to persist a vehicle signal" without
saying how.

An **adapter** is a concrete implementation that plugs into a port. Example:
`SqliteSignalStore` implements `SignalWriter` using SQLite. `InMemorySignalStore`
implements the same port using a Python list. The application never knows which
one is behind the port.

### Q: What is the composition root?

`main.py` — the one place that knows about all concrete adapters. It creates
them, wires them together, and starts the program. It sits **outside** the
hexagon and contains zero business logic. If you need to swap SQLite for
Postgres, you change `main.py` and nothing else.

### Q: How many ports should an application have?

Cockburn says it's a matter of taste — typically 2 to 4. This project has two:

- `SignalWriter` — persist signals (driven/secondary port)
- `SignalReader` — read signals from a data source (driven/secondary port)

A real instrument cluster might add:
- `AlarmNotifier` — push alerts to a display
- `ClusterRenderer` — draw gauges and indicators

### Q: What is the difference between driving and driven adapters?

| | Driving (primary) | Driven (secondary) |
|---|---|---|
| **Direction** | Calls INTO the application | Application calls OUT to it |
| **Who initiates** | The adapter | The application |
| **Examples** | CLI, Qt GUI, test harness, HTTP controller | Database, CAN bus, file system, external API |
| **In this project** | `adapters/driving/cli.py` | `SqliteSignalStore`, `MockCANReader`, `InMemorySignalStore` |

---

## Where Things Live

### Q: Where would a Qt GUI live?

`adapters/driving/qt_gui.py` — it's a **driving adapter**. It replaces the CLI
as the thing that drives the application. It would call the same use cases
(`record_signal`, `read_next_signal`) through the same ports. The application
layer and domain would not change at all.

### Q: Where would a real CAN bus reader live?

`adapters/driven/can_reader.py` — it's a **driven adapter** that implements
the `SignalReader` port. It would use something like `python-can` or SocketCAN
to read real vehicle signals instead of the hardcoded mock data. You'd swap it
in by changing one line in `main.py`.

### Q: Where would alarm/threshold logic live?

The **rules** (e.g., "coolant temp above 110°C = critical") are business logic,
so they go in `domain/`. The **use case** that checks signals against thresholds
goes in `application/services/`. The **notification mechanism** (buzzer, screen
flash, log entry) is a driven adapter behind a new `AlarmNotifier` port.

### Q: Where would configuration live (connection strings, thresholds, etc.)?

Behind a port. Define a `ConfigReader` protocol in `application/ports/`, then
implement it as a driven adapter — `adapters/driven/env_config.py` for
environment variables, `adapters/driven/yaml_config.py` for a config file, etc.
The application never knows where config comes from.

### Q: Where would logging or an audit trail live?

`adapters/driven/` — it's a driven adapter behind a `Logger` or `AuditWriter`
port. The application calls `logger.log(event)` through the port; the adapter
decides whether that goes to a file, a database, or stdout.

### Q: Where do tests live?

Next to the code they test, inside `tests/` subdirectories:

- `application/services/tests/` — use case tests (plugging in in-memory mocks)
- `adapters/driven/tests/` — integration tests for each driven adapter
- `adapters/driving/tests/` — tests for driving adapters (mocking I/O)

### Q: What if I need to add a REST API endpoint?

It's a driving adapter: `adapters/driving/rest_api.py`. It receives HTTP
requests and calls use cases, just like the CLI does. You'd wire it in
`main.py` alongside or instead of the CLI.

---

## Design Decisions

### Q: Why is `domain/` a separate top-level folder instead of inside `application/`?

This follows Clean Architecture's layering: `domain/` has zero dependencies
(not even on `application/`), while `application/services/` depends on `domain/`.
Keeping them as peers enforces the dependency rule by folder structure. Cockburn
himself has no concept of a domain layer — his hexagon is one undivided
"application" — but the separation prevents accidental coupling.

### Q: Why use Python's `Protocol` instead of `ABC`?

`Protocol` enables structural subtyping (duck typing with type checking).
Adapters don't need to explicitly inherit from the port — they just need to
have the right methods. This keeps adapters loosely coupled. `ABC` works too;
it's a style choice.

### Q: Why isn't there a factory class?

Factories are optional wiring helpers. In this project, `main.py` does the
wiring directly — it's simple enough that a factory would add indirection
without value. Factories become useful when adapter selection is complex
(e.g., choosing based on environment variables or feature flags).

### Q: How would you handle async / real-time data?

This is the biggest architectural decision for a real instrument cluster.
Options:

1. **Make ports async** — `async def read(self) -> VehicleSignal | None`
2. **Use a message bus / event loop** — adapters publish signals, use cases
   subscribe
3. **Thread-per-adapter** — common with Qt (`QThread` for CAN reading,
   main thread for rendering)

The hexagonal structure doesn't change — only the port signatures and the
concurrency mechanism in the composition root.

### Q: How does this relate to AUTOSAR?

AUTOSAR uses a layered architecture (Application, RTE, BSW) for embedded ECUs.
Hexagonal sits at a higher level — it's how you structure the **application
layer** that runs on top of AUTOSAR's Runtime Environment. The ports map to
AUTOSAR's sender-receiver or client-server interfaces; the adapters map to
Software Components (SWCs) that interact with the BSW through the RTE.

### Q: How would you scale this for a large team?

Each port + its adapters can be owned by a different team or developer. The
contract is the port interface — teams work independently as long as they
satisfy it. The composition root is the integration point where everything
comes together. This maps well to SAFe's component team structure.

---

## Testing

### Q: How do you test without real hardware?

That's the core value of the pattern. Every driven adapter has a mock/in-memory
counterpart:

| Real adapter | Test double | Port |
|---|---|---|
| `SqliteSignalStore` | `InMemorySignalStore` | `SignalWriter` |
| Real CAN bus (future) | `MockCANReader` | `SignalReader` |

Use case tests plug in the test doubles. No database, no CAN bus, no hardware.

### Q: What's the difference between unit tests and integration tests here?

- **Unit tests** (`application/services/tests/`) — test use cases with in-memory
  mocks. Fast, no I/O; verify business logic in isolation.
- **Integration tests** (`adapters/driven/tests/`) — test real adapters against
  real infrastructure (SQLite file, actual CAN socket). Verify the adapter
  fulfills the port contract.
- **Driving adapter tests** (`adapters/driving/tests/`) — test that the driving
  adapter correctly calls use cases and formats output. Mock the I/O boundary.

### Q: Can you run the full app without a database?

Yes. Change one line in `main.py`:

```python
writer = InMemorySignalStore()  # instead of SqliteSignalStore(...)
```

The application, use cases, and domain work identically. That's the point.
