"""Policy-controlled workflow with immutable JSONL audit records."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .classifier import KeywordClassifier
from .models import Decision, Ticket, WorkflowResult


class OpsCopilot:
    def __init__(
        self,
        audit_path: Path,
        classifier: KeywordClassifier | None = None,
        auto_route_threshold: float = 0.8,
    ) -> None:
        self.audit_path = audit_path
        self.classifier = classifier or KeywordClassifier()
        self.auto_route_threshold = auto_route_threshold

    def process(self, ticket: Ticket) -> WorkflowResult:
        triage = self.classifier.classify(ticket)
        sensitive = any(word in ticket.body.lower() for word in ("security", "legal", "refund"))
        decision = (
            Decision.AUTO_ROUTE
            if triage.confidence >= self.auto_route_threshold and not sensitive
            else Decision.NEEDS_APPROVAL
        )
        timestamp = datetime.now(UTC).isoformat()
        digest_input = f"{ticket.id}:{triage.category.value}:{decision.value}:{timestamp}"
        audit_id = hashlib.sha256(digest_input.encode()).hexdigest()[:12]
        result = WorkflowResult(ticket.id, triage, decision, audit_id)
        self._append_audit(timestamp, ticket, result)
        return result

    def _append_audit(self, timestamp: str, ticket: Ticket, result: WorkflowResult) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {"timestamp": timestamp, "ticket": asdict(ticket), "result": asdict(result)}
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")

