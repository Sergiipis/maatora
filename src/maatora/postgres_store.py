import contextlib
from typing import Any

import psycopg


class PostgresReceiptStore:
    def __init__(self, dsn: str) -> None:
        """Initializes the store with the database connection string."""
        self.dsn = dsn

    @contextlib.contextmanager
    def db_connection(self):
        conn = psycopg.connect(self.dsn)
        try:
            cur = conn.cursor()
            yield cur
        finally:
            conn.commit()
            conn.close()

    def init_schema(self) -> None:
        """Creates the 'receipts' table if it does not exist using the specified schema."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            payload JSONB,
            signature TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.db_connection() as cur:
            cur.execute(create_table_query)

    def append(self, receipt: dict[str, Any]) -> None:
        """
        Inserts a receipt record into the database using parameterized queries.
        Expected keys: 'id', 'action', 'actor_id', 'payload', 'signature'.
        """
        insert_query = """
        INSERT INTO receipts (id, action, actor_id, payload, signature)
        VALUES (%s, %s, %s, %s, %s);
        """
        with self.db_connection() as cur:
            cur.execute(
                insert_query,
                (
                    receipt["id"],
                    receipt["action"],
                    receipt["actor_id"],
                    receipt.get("payload"),
                    receipt.get("signature"),
                ),
            )

    def get(self, id: str) -> dict[str, Any] | None:
        """
        Retrieves a receipt by its unique ID.
        Returns a dictionary mapping column names to values if found, otherwise None.
        """
        select_query = "SELECT id, action, actor_id, payload, signature, created_at FROM receipts WHERE id = %s;"
        with self.db_connection() as cur:
            cur.execute(select_query, (id,))
            return dict(cur.fetchone())

    def list_by_actor(self, actor_id: str) -> list[dict[str, Any]]:
        """Retrieves all receipts for a specific actor as a list of dictionaries."""
        select_query = "SELECT id, action, actor_id, payload, signature, created_at FROM receipts WHERE actor_id = %s;"
        with self.db_connection() as cur:
            cur.execute(select_query, (actor_id,))
            return [dict(row) for row in cur.fetchall()]
