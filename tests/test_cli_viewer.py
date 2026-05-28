import json

import pytest

from maatora.cli_viewer import main


@pytest.fixture
def receipts(tmp_path):
    """Create a JSONL file with receipts."""
    receipts = [
        {"id": "rec1", "action": "send_email", "status": "success"},
        {"id": "rec2", "action": "query_db", "status": "failed"},
    ]
    file_path = tmp_path / "receipts.jsonl"
    with open(file_path, "w", encoding="utf-8") as f:
        for r in receipts:
            f.write(json.dumps(r) + "\n")
    return file_path


def test_list_receipts_from_file(receipts, capsys):
    """Test that 'list' command correctly displays receipts from a file."""
    # Execute
    exit_code = main(["-f", str(receipts), "list"])

    # Verify
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "rec1" in out
    assert "send_email" in out
    assert "success" in out
    assert "rec2" in out
    assert "query_db" in out
    assert "failed" in out


def test_show_receipt_success(receipts, capsys):
    """Test that 'show' command displays the full JSON of a specific receipt."""
    # Execute
    exit_code = main(["-f", str(receipts), "show", "rec1"])

    # Verify
    out = capsys.readouterr().out
    assert exit_code == 0
    parsed_out = json.loads(out)
    assert parsed_out["id"] == "rec1"
    assert parsed_out["action"] == "send_email"


def test_show_receipt_not_found(tmp_path, capsys, receipts):
    """Test that 'show' command returns error when ID does not exist."""
    # Setup
    file_path = tmp_path / "receipts.jsonl"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"id": "rec1", "action": "test", "status": "ok"}) + "\n")

    # Execute
    exit_code = main(["-f", str(file_path), "show", "nonexistent"])

    # Verify
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "Error: Receipt with ID 'nonexistent' not found." in err


def test_list_empty_file(tmp_path, capsys, receipts):
    """Test 'list' command behavior with an empty file."""
    file_path = tmp_path / "empty.jsonl"
    file_path.write_text("")

    exit_code = main(["-f", str(file_path), "list"])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "No receipts found." in out


def test_list_empty_file_with_stdin(tmp_path, capsys, receipts):
    """Test 'list' command behavior with an empty file and stdin."""
    file_path = tmp_path / "empty.jsonl"
    file_path.write_text("")

    exit_code = main(["-f", str(file_path), "list"])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "No receipts found." in out


def test_show_receipt_success_with_stdin(tmp_path, capsys, receipts):
    """Test that 'show' command displays the full JSON of a specific receipt when reading from stdin."""
    # Setup
    file_path = tmp_path / "receipts.jsonl"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"id": "rec1", "action": "send_email", "status": "success"}) + "\n")

    # Execute
    exit_code = main(["-f", str(file_path), "show", "rec1"])

    # Verify
    out = capsys.readouterr().out
    assert exit_code == 0
    parsed_out = json.loads(out)
    assert parsed_out["id"] == "rec1"
    assert parsed_out["action"] == "send_email"


def test_show_receipt_not_found_with_stdin(tmp_path, capsys, receipts):
    """Test that 'show' command returns error when ID does not exist and reading from stdin."""
    # Setup
    file_path = tmp_path / "receipts.jsonl"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"id": "rec1", "action": "test", "status": "ok"}) + "\n")

    # Execute
    exit_code = main(["-f", str(file_path), "show", "nonexistent"])

    # Verify
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "Error: Receipt with ID 'nonexistent' not found." in err
