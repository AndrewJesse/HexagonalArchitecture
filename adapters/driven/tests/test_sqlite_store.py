# Integration tests for the SQLite adapter.
#
# These verify the concrete adapter actually reads/writes to a real
# SQLite database. In Ports & Adapters, integration tests target the
# outermost ring to prove the adapter fulfills the port contract.
import os
import tempfile
import unittest

from adapters.driven.sqlite_store import SqliteStore
from domain.transform import Payload


class TestSqliteStore(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.store = SqliteStore(self._tmp.name)

    def tearDown(self) -> None:
        os.unlink(self._tmp.name)

    def test_write_persists_payload(self) -> None:
        payload = Payload(text="hello", date="2026-01-01T00:00:00")
        self.store.write(payload)

        cur = self.store._conn.execute("SELECT text, date FROM payload")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "hello")
        self.assertEqual(row[1], "2026-01-01T00:00:00")

    def test_write_multiple_payloads(self) -> None:
        self.store.write(Payload(text="a", date="2026-01-01T00:00:00"))
        self.store.write(Payload(text="b", date="2026-01-02T00:00:00"))

        cur = self.store._conn.execute("SELECT COUNT(*) FROM payload")
        self.assertEqual(cur.fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
