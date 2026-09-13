"""Explainable local baseline behind a replaceable classifier boundary."""

from __future__ import annotations

from collections import defaultdict

from .models import Category, Ticket, Triage

KEYWORDS = {
    Category.BILLING: {"invoice", "refund", "charged", "payment", "billing"},
    Category.ACCESS: {"login", "password", "locked", "access", "sign-in"},
    Category.INCIDENT: {"down", "outage", "error", "unavailable", "broken"},
}
QUEUES = {
    Category.BILLING: "finance-support",
    Category.ACCESS: "identity-support",
    Category.INCIDENT: "incident-response",
    Category.GENERAL: "customer-support",
}


class KeywordClassifier:
    def classify(self, ticket: Ticket) -> Triage:
        text = f"{ticket.subject} {ticket.body}".lower()
        scores: dict[Category, int] = defaultdict(int)
        matched: dict[Category, list[str]] = defaultdict(list)
        for category, keywords in KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
                    matched[category].append(keyword)
        category = max(scores, key=scores.get) if scores else Category.GENERAL
        hits = scores.get(category, 0)
        confidence = min(0.55 + hits * 0.15, 0.95) if hits else 0.35
        urgent = any(word in text for word in ("urgent", "production", "all users", "security"))
        priority = 1 if category is Category.INCIDENT and urgent else 2 if urgent else 3
        rationale = (
            f"Matched keywords: {', '.join(sorted(matched[category]))}"
            if hits
            else "No category-specific keywords matched"
        )
        return Triage(category, confidence, priority, QUEUES[category], rationale)

