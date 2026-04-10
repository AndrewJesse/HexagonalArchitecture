# Domain Layer — pure data structures and business rules.
#
# In Clean Architecture this is the innermost layer, independent of
# everything else.  In Cockburn's hexagonal architecture, domain is
# simply part of "the application" — but kept in its own top-level
# folder here so the dependency rule is enforced by structure:
#
#   domain/  ← depends on nothing
#   application/  ← depends on domain
#   adapters/  ← depends on domain + application
from dataclasses import dataclass


@dataclass
class Payload:
    text: str = ""
    date: str | None = None
