from __future__ import annotations
from abc import ABC, abstractmethod

# Application port: exposes tax calculation use case to driving side.
class ForCalculatingTaxes(ABC):
    @abstractmethod
    def tax_on(self, amount: float) -> float:
        pass

# Application port: abstracts how tax rates are retrieved.
class ForGettingTaxRates(ABC):
    @abstractmethod
    def tax_rate(self, amount: float) -> float:
        pass

# Service core business logic depending only on ports.
class TaxCalculator(ForCalculatingTaxes):
    def __init__(self, tax_rate_repository: ForGettingTaxRates) -> None:
        self.tax_rate_repository = tax_rate_repository

    def tax_on(self, amount: float) -> float:
        return amount * self.tax_rate_repository.tax_rate(amount)

# Adapter: concrete infrastructure implementation for tax rates.
class FixedTaxRateRepository(ForGettingTaxRates):
    def tax_rate(self, amount: float) -> float:
        return 0.15

# Composition root: wires adapters into the application and runs use case.
def main() -> None:
    tax_rate_repository: ForGettingTaxRates = FixedTaxRateRepository()
    my_calculator = TaxCalculator(tax_rate_repository)
    print(my_calculator.tax_on(100))

# Runtime entry point: starts the composed application.
if __name__ == "__main__":
    main()
