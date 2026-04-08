from pathlib import Path
import sqlite3

from model.transform import Payload


class SqliteStore:
    def __init__(self, path: str = "app.db") -> None:
        self._repo_root = Path(__file__).resolve().parent.parent
        self._migrations_dir = self._repo_root / "data" / "sql" / "migrations"
        self._queries_dir = self._repo_root / "data" / "sql" / "queries"

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._run_migrations()

    def _query_sql(self, name: str) -> str:
        return (self._queries_dir / name).read_text(encoding="utf-8")

    def _run_migrations(self) -> None:
        if not self._migrations_dir.exists():
            return
        if not self._conn.execute(
            self._query_sql("select_schema_migrations_table_exists.sql")
        ).fetchone():
            ddl_000 = self._migrations_dir / "000_create_schema_migrations_table.sql"
            if ddl_000.exists():
                self._conn.executescript(ddl_000.read_text(encoding="utf-8"))
                self._conn.execute(
                    self._query_sql("insert_migration.sql"),
                    (ddl_000.name,),
                )
        migrations = sorted(self._migrations_dir.glob("*.sql"))
        for migration in migrations:
            already_applied = self._conn.execute(
                self._query_sql("select_migration_applied.sql"),
                (migration.name,),
            ).fetchone()
            if already_applied:
                continue

            sql = migration.read_text(encoding="utf-8")
            self._conn.executescript(sql)
            self._conn.execute(
                self._query_sql("insert_migration.sql"),
                (migration.name,),
            )

        has_payload_table = self._conn.execute(
            self._query_sql("select_payload_table_exists.sql")
        ).fetchone()
        if not has_payload_table:
            bootstrap = self._migrations_dir / "001_create_memo_table.sql"
            if bootstrap.exists():
                self._conn.executescript(bootstrap.read_text(encoding="utf-8"))
                self._conn.execute(
                    self._query_sql("insert_migration_ignore.sql"),
                    (bootstrap.name,),
                )
        self._conn.commit()

    def write(self, data: Payload) -> None:
        self._conn.execute(
            self._query_sql("insert_payload.sql"),
            (data.text, data.date),
        )
        self._conn.commit()
