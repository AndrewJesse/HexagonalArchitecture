from pathlib import Path
import sqlite3

from model.transform import Payload


class SqliteStore:
    def __init__(self, path: str = "app.db") -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._run_migrations()

    def _run_migrations(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                name TEXT PRIMARY KEY
            )
            """
        )
        # Load migrations from the current project layout.
        repo_root = Path(__file__).resolve().parent.parent
        migrations_dir = repo_root / "data" / "sql"
        if not migrations_dir.exists():
            return
        migrations = sorted(migrations_dir.glob("*.sql"))
        for migration in migrations:
            already_applied = self._conn.execute(
                "SELECT 1 FROM schema_migrations WHERE name = ?",
                (migration.name,),
            ).fetchone()
            if already_applied:
                continue

            sql = migration.read_text(encoding="utf-8")
            self._conn.executescript(sql)
            self._conn.execute(
                "INSERT INTO schema_migrations (name) VALUES (?)",
                (migration.name,),
            )

        has_payload_table = self._conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='payload'"
        ).fetchone()
        if not has_payload_table:
            bootstrap = migrations_dir / "0001_create_payload.sql"
            if bootstrap.exists():
                self._conn.executescript(bootstrap.read_text(encoding="utf-8"))
                self._conn.execute(
                    "INSERT OR IGNORE INTO schema_migrations (name) VALUES (?)",
                    (bootstrap.name,),
                )
        self._upgrade_legacy_single_row_payload_table()
        self._conn.commit()

    def _upgrade_legacy_single_row_payload_table(self) -> None:
        row = self._conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='payload'"
        ).fetchone()
        if not row or not row[0]:
            return
        if "CHECK (id = 1)" not in row[0]:
            return

        self._conn.executescript(
            """
            CREATE TABLE payload_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                date DATETIME NOT NULL
            );

            INSERT INTO payload_v2 (text, date)
            SELECT text, date
            FROM payload;

            DROP TABLE payload;

            ALTER TABLE payload_v2 RENAME TO payload;
            """
        )

    def write(self, data: Payload) -> None:
        self._conn.execute(
            """
            INSERT INTO payload (text, date)
            VALUES (?, ?)
            """,
            (data.text, data.date),
        )
        self._conn.commit()
