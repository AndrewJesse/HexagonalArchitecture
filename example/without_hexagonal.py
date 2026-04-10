"""Discount calculator WITHOUT hexagonal architecture.
The rate logic is hardcoded directly inside the Discounter class.
No ports, no adapters, no dependency injection.
"""


class Discounter:
    def discount(self, amount: float) -> float:
        rate = self._get_rate(amount)
        return amount * rate

    def _get_rate(self, amount: float) -> float:
        # Rate logic baked directly into the application — not replaceable
        if amount <= 100:
            return 0.01
        if amount <= 1000:
            return 0.02
        return 0.05


# ---------- Tests (tightly coupled to the one implementation) ----------

def test_discounter():
    app = Discounter()
    assert app.discount(100) == 1.0,   f"Expected 1.0, got {app.discount(100)}"
    assert app.discount(200) == 4.0,   f"Expected 4.0, got {app.discount(200)}"
    assert app.discount(5000) == 250.0, f"Expected 250.0, got {app.discount(5000)}"
    print("All tests passed.")


# ---------- Simple CLI "UI" ----------

def main():
    app = Discounter()
    amount = float(input("Enter amount: "))
    print(f"Discount on {amount} is {app.discount(amount)}")


if __name__ == "__main__":
    test_discounter()
    main()
