from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .models import Ticket
from .workflow import OpsCopilot


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage a support ticket with policy guardrails")
    parser.add_argument("subject")
    parser.add_argument("body")
    parser.add_argument("--ticket-id", default="demo-001")
    parser.add_argument("--audit-log", type=Path, default=Path("audit/events.jsonl"))
    args = parser.parse_args()
    result = OpsCopilot(args.audit_log).process(Ticket(args.ticket_id, args.subject, args.body))
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()

