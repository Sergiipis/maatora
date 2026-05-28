from maatora.html_summary_renderer import render


def test_default_template() -> None:
    """Verifies rendering with default template and complete data."""
    receipt = {
        "actor_id": "agent-007",
        "action": "Search Web",
        "timestamp": "2023-10-27T10:00:00Z",
        "cost_usd": "0.01",
    }
    expected = "<p>Agent agent-007 performed Search Web at 2023-10-27T10:00:00Z (cost: $0.01).</p>"
    assert render(receipt) == expected


def test_custom_template() -> None:
    """Verifies rendering with a user-provided template string."""
    receipt = {"user": "Alice", "status": "Success"}
    template = "<div>User {{ user }} performed {{ status }}</div>"
    expected = "<div>User Alice performed Success</div>"
    assert render(receipt, template=template) == expected


def test_xss_escaping() -> None:
    """Verifies that HTML tags in receipt data are properly escaped."""
    receipt = {
        "actor_id": "<script>alert('xss')</script>",
        "action": "<b>Bold Action</b>",
        "timestamp": "2023-10-27",
        "cost_usd": "0.00",
    }
    result = render(receipt)

    assert "<script>" not in result
    assert "<b>" not in result
    assert "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in result
    assert "&lt;b&gt;Bold Action&lt;/b&gt;" in result


def test_missing_fields_na() -> None:
    """Verifies that missing keys in the receipt dictionary are rendered as 'N/A'."""
    receipt = {"actor_id": "agent-001", "action": "Data Fetch"}
    expected = "<p>Agent agent-001 performed Data Fetch at N/A (cost: $N/A).</p>"
    assert render(receipt) == expected
