from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Evidence:
    source: str
    query: str
    observation: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reliability: float = 1.0

@dataclass
class Hypothesis:
    name: str
    score: float = 0.0
    supporting: list[str] = field(default_factory=list)
    contradicting: list[str] = field(default_factory=list)

@dataclass
class InvestigationState:
    incident: str
    namespace: str
    evidence: list[Evidence] = field(default_factory=list)
    hypotheses: dict[str, Hypothesis] = field(default_factory=dict)
    timeline: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)
    iterations: int = 0
