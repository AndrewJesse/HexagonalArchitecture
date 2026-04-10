"""Discount calculator WITH hexagonal architecture (ports & adapters).

Reading guide:
  Definitions are ordered so Python can run top-to-bottom.
  Follow the numbered ──▶ arrows to trace the execution flow.

  Execution starts at step 1 (bottom of file), then jumps UP to the
  functions/classes it calls. Think of it like a stack: entry point
  at the bottom, deepest dependency at the top.

Key idea:
  The core application (Discounter) never imports or mentions a concrete
  database / mock.  It only depends on the PORT (RateRepository ABC).
  Adapters are plugged in from the outside — that's dependency inversion.
"""

from abc import ABC, abstractmethod


# =====================================================================
# DEEPEST LAYER: PORT — application/ports/
#
#    The INTERFACE (abstract base class) that defines what the
#    application NEEDS from the outside world.  Called a "port"
#    because it's the plug-socket on the hexagon boundary.
#
#    The core codes against THIS, never against a concrete
#    database or mock.  The core doesn't know (or care) what's
#    on the other side.
# =====================================================================

class RateRepository(ABC):
    @abstractmethod
    def get_rate(self, amount: float) -> float: ...


# =====================================================================
# ADAPTER (driven side) — adapters/
#
#    A concrete implementation of the port.  This one is an in-memory
#    fake ("mock") useful for testing and demos.
#
#    Tomorrow you could write PostgresRateRepository that hits a real
#    database — it just needs to implement the same get_rate() method.
#    Nothing else in the codebase changes.
#
#    ◀── called by step 4 (Discounter.discount → self._rate_repository.get_rate)
# =====================================================================

class 
(RateRepository):
    def get_rate(self, amount: float) -> float:
        # Simple tiered-rate logic standing in for a real DB lookup.
        # This is the deepest call in the chain — the actual data source.
        if amount <= 100:
            return 0.01
        if amount <= 1000:
            return 0.02
        return 0.05


# =====================================================================
# FACTORY (optional wiring helper) — adapters/
#
#    Centralises the decision of WHICH adapter to create.
#    NOT an adapter itself — just convenience glue.
#    You could skip this and write MockRateRepository() directly.
#
#    ◀── called by step 2 (test_discounter) and step 3 (main)
# =====================================================================

class RepositoryFactory:
    @staticmethod
    def get_mock_rate_repository() -> RateRepository:
        # Returns a RateRepository — caller doesn't know the concrete class
        return MockRateRepository()

    # @staticmethod
    # def get_real_rate_repository(conn_str: str) -> RateRepository:
    #     return PostgresRateRepository(conn_str)   # swap in when ready


# =====================================================================
# APPLICATION CORE (the hexagon) — application/services/
#
#    The business logic.  Notice:
#      - Constructor takes RateRepository (the PORT), not a concrete class.
#      - discount() calls self._rate_repository.get_rate() — it has
#        NO IDEA which adapter is behind it.
#
#    That's dependency inversion: the core defines the interface,
#    the outside world provides the implementation.
#
#    ◀── created by step 2 and step 3
#    ◀── .discount() called by step 2 and step 3
# =====================================================================

class Discounter:
    def __init__(self, rate_repository: RateRepository) -> None:
        # Dependency injection — the adapter is passed IN, not created here
        self._rate_repository = rate_repository

    def discount(self, amount: float) -> float:
        # Step 4: calls the PORT interface — could be mock, postgres, anything
        #         ──▶ MockRateRepository.get_rate() (the adapter above)
        rate = self._rate_repository.get_rate(amount)
        return amount * rate


# =====================================================================
# STEP 2 — DRIVING ADAPTER: test harness — tests/ or example/
#
#    A "driving" (user-side) adapter: it DRIVES the application.
#    Wires up a mock adapter via the factory, then exercises the core.
#
#    Because the adapter is injected, we can test real Discounter logic
#    without a database, network, or any external dependency.
# =====================================================================

def test_discounter():
    # ──▶ Factory creates the driven-side adapter (mock DB)
    # ──▶ Adapter is injected into the core application
    app = Discounter(RepositoryFactory.get_mock_rate_repository())

    # ──▶ Drive the application and verify results
    assert app.discount(100) == 1.0,   f"Expected 1.0, got {app.discount(100)}"
    assert app.discount(200) == 4.0,   f"Expected 4.0, got {app.discount(200)}"
    assert app.discount(5000) == 250.0, f"Expected 250.0, got {app.discount(5000)}"
    print("All tests passed.")


# =====================================================================
# STEP 3 — DRIVING ADAPTER: CLI / UI — main.py / __main__.py
#
#    Another driving adapter — same wiring pattern, different interface.
#    The user types an amount, the adapter feeds it into the core,
#    and displays the result.
#
#    Swapping MockRateRepository for a real DB = ONE-LINE change
#    (change the factory call).  Discounter stays untouched.
# =====================================================================

def main():
    # ──▶ Factory picks the adapter, inject it into the core
    repo = RepositoryFactory.get_mock_rate_repository()
    app = Discounter(repo)

    # ──▶ Drive the application with user input
    amount = float(input("Enter amount: "))
    print(f"Discount on {amount} is {app.discount(amount)}")


# =====================================================================
# STEP 1 — ENTRY POINT: execution starts here
#
#    Python runs this block when you execute the script directly.
#    It calls the two driving adapters in order:
#      ──▶ test_discounter()  (step 2)
#      ──▶ main()             (step 3)
# =====================================================================

if __name__ == "__main__":
    test_discounter()
    main()
