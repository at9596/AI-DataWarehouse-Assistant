"""
tests/test_connection.py
--------------------------
Unit tests for database/connection.py.

Covers:
  - get_connection() in DEMO_MODE → returns None
  - get_connection() in live mode → delegates to pyodbc
  - test_connection() in DEMO_MODE → (True, "Demo Mode")
  - test_connection() live success → (True, message with DB name)
  - test_connection() live failure → (False, error message)
"""
import pytest
from unittest.mock import MagicMock, patch


# ── get_connection ────────────────────────────────────────────────────────────

class TestGetConnection:
    def test_demo_mode_returns_none(self, mocker):
        mocker.patch("database.connection.DEMO_MODE", True)
        from database.connection import get_connection
        assert get_connection() is None

    def test_live_mode_returns_connection_object(self, mocker):
        mock_conn = MagicMock()
        # Inject mock pyodbc into sys.modules BEFORE the lazy import runs
        mock_pyodbc = MagicMock()
        mock_pyodbc.connect.return_value = mock_conn
        mocker.patch.dict("sys.modules", {"pyodbc": mock_pyodbc})
        mocker.patch("database.connection.DEMO_MODE", False)

        from database.connection import get_connection
        result = get_connection()
        assert result == mock_conn

    def test_live_mode_builds_correct_connection_string(self, mocker):
        """Ensure SERVER, DATABASE, UID, PWD are all in the connection string."""
        captured_conn_str = {}

        def fake_connect(conn_str):
            captured_conn_str["value"] = conn_str
            return MagicMock()

        # Inject mock pyodbc BEFORE the lazy import fires
        mock_pyodbc = MagicMock()
        mock_pyodbc.connect.side_effect = fake_connect
        mocker.patch.dict("sys.modules", {"pyodbc": mock_pyodbc})

        # Patch module-level constants used to build the conn string
        mocker.patch("database.connection.DEMO_MODE",   False)
        mocker.patch("database.connection.DB_SERVER",   "my-server")
        mocker.patch("database.connection.DB_DATABASE", "MyDB")
        mocker.patch("database.connection.DB_USERNAME", "myuser")
        mocker.patch("database.connection.DB_PASSWORD", "secret")

        from database.connection import get_connection
        get_connection()

        cs = captured_conn_str.get("value", "")
        assert "my-server" in cs
        assert "MyDB"      in cs
        assert "myuser"    in cs
        assert "secret"    in cs


# ── test_connection ───────────────────────────────────────────────────────────

class TestTestConnection:
    def test_demo_mode_returns_true(self, mocker):
        mocker.patch("database.connection.DEMO_MODE", True)
        from database.connection import test_connection
        success, msg = test_connection()
        assert success is True

    def test_demo_mode_message_mentions_demo(self, mocker):
        mocker.patch("database.connection.DEMO_MODE", True)
        from database.connection import test_connection
        _, msg = test_connection()
        assert "Demo Mode" in msg or "demo" in msg.lower()

    def test_live_success_returns_true(self, mocker):
        mock_conn = MagicMock()
        mocker.patch("database.connection.DEMO_MODE", False)
        mocker.patch("database.connection.get_connection", return_value=mock_conn)

        from database.connection import test_connection
        success, msg = test_connection()
        assert success is True

    def test_live_success_closes_connection(self, mocker):
        mock_conn = MagicMock()
        mocker.patch("database.connection.DEMO_MODE", False)
        mocker.patch("database.connection.get_connection", return_value=mock_conn)

        from database.connection import test_connection
        test_connection()
        mock_conn.close.assert_called_once()

    def test_live_success_message_contains_db_name(self, mocker):
        mock_conn = MagicMock()
        mocker.patch("database.connection.DEMO_MODE", False)
        mocker.patch("database.connection.DB_DATABASE", "SalesWarehouse")
        mocker.patch("database.connection.get_connection", return_value=mock_conn)

        from database.connection import test_connection
        _, msg = test_connection()
        assert "SalesWarehouse" in msg

    def test_live_failure_returns_false(self, mocker):
        mocker.patch("database.connection.DEMO_MODE", False)
        mocker.patch("database.connection.get_connection",
                     side_effect=Exception("host unreachable"))

        from database.connection import test_connection
        success, _ = test_connection()
        assert success is False

    def test_live_failure_message_contains_error(self, mocker):
        mocker.patch("database.connection.DEMO_MODE", False)
        mocker.patch("database.connection.get_connection",
                     side_effect=Exception("host unreachable"))

        from database.connection import test_connection
        _, msg = test_connection()
        assert "Connection failed" in msg or "host unreachable" in msg

    @pytest.mark.parametrize("error_msg", [
        "timeout",
        "Login failed for user 'sa'",
        "Cannot open server 'xyz'",
    ])
    def test_various_db_errors_return_false(self, mocker, error_msg):
        mocker.patch("database.connection.DEMO_MODE", False)
        mocker.patch("database.connection.get_connection",
                     side_effect=Exception(error_msg))

        from database.connection import test_connection
        success, _ = test_connection()
        assert success is False
