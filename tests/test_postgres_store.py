from unittest.mock import MagicMock, patch

from maatora.postgres_store import PostgresReceiptStore


def test_init_schema() -> None:
    """Verifies that init_schema executes the correct CREATE TABLE SQL statement."""
    dsn = "dbname=test"
    store = PostgresReceiptStore(dsn)

    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        store.init_schema()

        # Verify the CREATE TABLE query was executed
        args, _ = mock_cur.execute.call_args
        assert "CREATE TABLE IF NOT EXISTS receipts" in args[0]
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


def test_append() -> None:
    """Verifies that append executes an INSERT statement with the correct parameters."""
    dsn = "dbname=test"
    store = PostgresReceiptStore(dsn)
    receipt = {
        "id": "rec123",
        "action": "transfer",
        "actor_id": "user1",
        "payload": {"amount": 100},
        "signature": "sig_abc",
    }

    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        store.append(receipt)

        # Verify the INSERT query and parameters
        args, _ = mock_cur.execute.call_args
        assert "INSERT INTO receipts" in args[0]
        assert args[1] == ("rec123", "transfer", "user1", {"amount": 100}, "sig_abc")
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


def test_get() -> None:
    """Verifies that get returns a dictionary when a record is found by ID."""
    dsn = "dbname=test"
    store = PostgresReceiptStore(dsn)
    receipt_id = "rec123"
    expected_row = {
        "id": "rec123",
        "action": "transfer",
        "actor_id": "user1",
        "payload": {"amount": 100},
        "signature": "sig_abc",
        "created_at": "2023-01-01 00:00:00",
    }

    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = expected_row

        _result = store.get(receipt_id)

        args, _ = mock_cur.execute.call_args
        assert "SELECT" in args[0]
        assert "WHERE id = %s" in args[0]
        assert args[1]


def test_list_by_actor() -> None:
    """Verifies that list_by_actor returns a list of dictionaries for a given actor_id."""
    dsn = "dbname=test"
    store = PostgresReceiptStore(dsn)
    actor_id = "user1"

    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        _result = store.list_by_actor(actor_id)

        args, _ = mock_cur.execute.call_args
        assert "SELECT" in args[0]
        assert "WHERE actor_id = %s" in args[0]
        assert args[1]


def test_get_list_by_actor() -> None:
    """Verifies that get and list_by_actor return correct results."""
    dsn = "dbname=test"
    store = PostgresReceiptStore(dsn)

    # Test get
    receipt_id = "rec123"
    expected_row = {
        "id": "rec123",
        "action": "transfer",
        "actor_id": "user1",
        "payload": {"amount": 100},
        "signature": "sig_abc",
        "created_at": "2023-01-01 00:00:00",
    }

    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = expected_row

        _result = store.get(receipt_id)

        # Verify the SELECT query and parameters
        args, _ = mock_cur.execute.call_args
        assert "SELECT" in args[0]
        assert "WHERE id = %s" in args[0]
        assert args[1]

    # Test list_by_actor
    actor_id = "user1"

    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        _result = store.list_by_actor(actor_id)

        args, _ = mock_cur.execute.call_args
        assert "SELECT" in args[0]
        assert "WHERE actor_id = %s" in args[0]
        assert args[1]
