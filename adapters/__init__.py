# Adapters Layer — the outermost ring of the hexagon.
#
# Adapters are split into two categories following Cockburn's terminology:
#
#   driving/  (primary adapters, LEFT side of hexagon)
#     — Things that DRIVE the application: CLI, GUI, test harnesses, HTTP
#       controllers.  They call into the application's use cases.
#
#   driven/   (secondary adapters, RIGHT side of hexagon)
#     — Things the application DRIVES: databases, file systems, external
#       APIs, message queues.  They implement the port interfaces.
#
# The application layer never imports from adapters — only the
# composition root (main.py) wires them together.
