# Unit tests for the application layer (use cases).
#
# These test the core business logic by plugging in the InMemoryStore
# adapter, so no real I/O occurs. In Ports & Adapters this proves the
# use case works independently of any infrastructure.
import unittest

from adapters.driven.in_memory_store import InMemoryStore
from application.services import write_user_input


class TestWriteUserInput(unittest.TestCase):
    def test_writes_trimmed_text_to_test_adaptor(self) -> None:
        store = InMemoryStore()
        saved = write_user_input(store, "  hello  ")
        self.assertEqual(saved.text, "hello")
        self.assertIsNotNone(saved.date)
        self.assertEqual(store.last().text, "hello")


if __name__ == "__main__":
    unittest.main()
