#===============================================
# Imports
#===============================================
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

#===============================================
# Domain
#===============================================
@dataclass(frozen=True)
class ConversionRate:
    value: float


@dataclass(frozen=True)
class Speed:
    kph: float


@dataclass(frozen=True)
class MilesPerHour:
    value: float


#===============================================
# Ports
#===============================================
class ForConvertingKphToMph(ABC):
    @abstractmethod
    def convert(self, speed: Speed) -> MilesPerHour:
        pass


class ForGettingConversionRate(ABC):
    @abstractmethod
    def conversion_rate(self) -> ConversionRate:
        pass


class ForGettingKilometersPerHour(ABC):
    @abstractmethod
    def kilometers_per_hour(self) -> Speed:
        pass


#===============================================
# Services
#===============================================
class SpeedConverter(ForConvertingKphToMph):
    def __init__(self, fixed_conversion_rate_repository: ForGettingConversionRate) -> None:
        self.fixed_conversion_rate_repository = fixed_conversion_rate_repository

    def convert(self, speed: Speed) -> MilesPerHour:
        rate = self.fixed_conversion_rate_repository.conversion_rate().value
        return MilesPerHour(value=rate * speed.kph)


#===============================================
# Adapters
#===============================================
class FixedConversionRateRepository(ForGettingConversionRate):
    def conversion_rate(self) -> ConversionRate:
        return ConversionRate(value=0.621371)


class KilometersPerHourRepository(ForGettingKilometersPerHour):
    def kilometers_per_hour(self) -> Speed:
        return Speed(kph=100)


#===============================================
# Composition Root
#===============================================
if __name__ == "__main__":
    conversion_rate_repository: ForGettingConversionRate = FixedConversionRateRepository()
    kilometers_per_hour_repository: ForGettingKilometersPerHour = KilometersPerHourRepository()
    my_conversion = SpeedConverter(conversion_rate_repository)

    print(my_conversion.convert(kilometers_per_hour_repository.kilometers_per_hour()))
