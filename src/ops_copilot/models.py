from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    BILLING = "billing"
    ACCESS = "access"
    INCIDENT = "incident"
    GENERAL = "general"


class Decision(str, Enum):
    AUTO_ROUTE = "auto_route"
    NEEDS_APPROVAL = "needs_approval"


@dataclass(frozen=True)
class Ticket:
    id: str
    subject: str
    body: str


@dataclass(frozen=True)
class Triage:
    category: Category
    confidence: float
    priority: int
    queue: str
    rationale: str


@dataclass(frozen=True)
class WorkflowResult:
    ticket_id: str
    triage: Triage
    decision: Decision
    audit_id: str

