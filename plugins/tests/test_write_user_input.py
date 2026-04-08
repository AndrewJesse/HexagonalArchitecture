import unittest

from plugins.memory import InMemoryStore
from app.pipeline import write_user_input


class TestWriteUserInput(unittest.TestCase):
    def test_writes_trimmed_text_to_test_adaptor(self) -> None:
        store = InMemoryStore()
        saved = write_user_input(store, "  hello  ")
        self.assertEqual(saved.text, "hello")
        self.assertIsNotNone(saved.date)
        self.assertEqual(store.last().text, "hello")


if __name__ == "__main__":
    unittest.main()
