import json

from ops_copilot.models import Category, Decision, Ticket
from ops_copilot.workflow import OpsCopilot


def test_high_confidence_ticket_is_auto_routed(tmp_path) -> None:
    log = tmp_path / "audit.jsonl"
    ticket = Ticket("t1", "Login access", "My login password is locked and I need access")
    result = OpsCopilot(log).process(ticket)
    assert result.triage.category is Category.ACCESS
    assert result.decision is Decision.AUTO_ROUTE
    assert json.loads(log.read_text())["result"]["audit_id"] == result.audit_id


def test_sensitive_ticket_requires_human_approval(tmp_path) -> None:
    ticket = Ticket("t2", "Refund invoice", "I was charged twice and need a refund")
    result = OpsCopilot(tmp_path / "audit.jsonl").process(ticket)
    assert result.triage.category is Category.BILLING
    assert result.decision is Decision.NEEDS_APPROVAL


def test_low_confidence_ticket_requires_approval(tmp_path) -> None:
    ticket = Ticket("t3", "Question", "Could somebody help me?")
    result = OpsCopilot(tmp_path / "audit.jsonl").process(ticket)
    assert result.decision is Decision.NEEDS_APPROVAL

