from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


# --- Domain (value objects + domain behavior) ---

@dataclass(frozen=True)
class Money:
    amount: float

    def multiplied_by(self, rate: TaxRate) -> Money:
        return Money(amount=self.amount * rate.value)


@dataclass(frozen=True)
class TaxRate:
    """Rate as a decimal, e.g. 0.15 for 15%."""

    value: float


# --- Application ports ---

# Driving port: use case exposed to the outside.
class ForCalculatingTaxes(ABC):
    @abstractmethod
    def tax_on(self, amount: Money) -> Money:
        pass


# Driven port: how we obtain a tax rate for a taxable amount.
class ForGettingTaxRates(ABC):
    @abstractmethod
    def tax_rate_for(self, taxable_amount: Money) -> TaxRate:
        pass


# --- Application service (orchestrates domain; depends only on ports) ---

class TaxCalculator(ForCalculatingTaxes):
    def __init__(self, tax_rate_repository: ForGettingTaxRates) -> None:
        self._tax_rates = tax_rate_repository

    def tax_on(self, amount: Money) -> Money:
        rate = self._tax_rates.tax_rate_for(amount)
        return amount.multiplied_by(rate)


# --- Adapter ---

class FixedTaxRateRepository(ForGettingTaxRates):
    def tax_rate_for(self, taxable_amount: Money) -> TaxRate:
        return TaxRate(value=0.15)


# --- Composition root ---

def main() -> None:
    tax_rate_repository: ForGettingTaxRates = FixedTaxRateRepository()
    calculator = TaxCalculator(tax_rate_repository)
    print(calculator.tax_on(Money(amount=100.0)))


if __name__ == "__main__":
    main()