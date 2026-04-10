# Domain Layer — the innermost part of the application hexagon.
#
# Domain objects are pure data structures and business rules.
# They have ZERO dependencies on ports, adapters, or any framework.
# Ports and services may import from domain, but domain never imports
# from anything outside itself.
from dataclasses import dataclass


@dataclass
class Payload:
    text: str = ""
    date: str | None = None
