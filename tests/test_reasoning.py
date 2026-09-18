from rca_agent.reasoner import InvestigationReasoner
from rca_agent.models import InvestigationState, Evidence

def test_next_query_is_evidence_gap_driven():
    r = InvestigationReasoner()
    s = InvestigationState("checkout has 5xx", "rca-demo")
    assert r.next_query(s) == "pods"
    s.evidence.append(Evidence("kubernetes", "list pods", "2 running"))
    assert r.next_query(s) == "events"

def test_oom_updates_hypothesis():
    r = InvestigationReasoner()
    s = InvestigationState("memory issue", "rca-demo")
    for h in r.initial_hypotheses(s.incident): s.hypotheses[h.name] = h
    s.evidence.append(Evidence("events", "list events", "container was OOMKilled"))
    r.update(s)
    assert s.hypotheses["resource exhaustion"].score > 0
