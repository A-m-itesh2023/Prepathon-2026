# Mid-Term Findings & Intended Approach

## Agentic Customer 360 — Proactive Intervention Desk

**Participant:** Amitesh Mitra  
**Roll No.:** 26055002  
**Branch:** Industrial Chemistry  
**Submission:** Mid-Term

### What I understood from the problem

The main challenge in this PS is not ordinary classification and not a chatbot. The system has to continuously process an asynchronous customer event stream, remember what "normal" looks like for that customer, combine weak evidence across multiple sources, infer an evolving customer state and finally make a bounded decision such as `no_action`, retention outreach, escalation, personalized offer, support intervention or fraud/compliance hold.

The supplied schema makes **event time** important because `ingestion_time` can differ and events may arrive late or out of order. We therefore plan to load the historical seed first, establish customer baselines, and process/reconcile live events using `event_time` rather than trusting arrival order.

### What I found from the practice scenarios

The three scenarios expose different versions of the same reasoning problem.

In Scenario 1, a stable historical income pattern changes while healthcare expenses, a hardship-related search and an explicit support request accumulate. Some large transfers/refunds are misleading when viewed alone. In Scenario 2, early evidence is weak: reduced income and baby-related spending gradually become much stronger when a child-savings search, daycare instruction and KYC dependents change appear. A support interaction also explains a large electronics purchase, showing that one source can **contradict** a false hypothesis produced from another. Scenario 3 is longitudinal: a rejected fee complaint is followed by lower engagement and progressive withdrawal of the banking relationship, while a tax refund temporarily makes the balance look healthier. This means point anomalies alone are not enough; trends and historical context matter.

Our main conclusion is:

**Event → source-specific signal → baseline comparison → shared customer state → competing hypotheses → synthesis → action policy → HITL/guardrail → auditable output**

### Preliminary architecture

We plan a hybrid multi-agent system. Four parallel specialists — **Transaction/Billing, Usage/Engagement, Support/Sentiment and KYC/Profile** — consume only their relevant sources and publish structured findings to a **per-customer state board**. They do not exchange unrestricted reasoning traces.

A **Synthesis/Life-Event Agent** reads these findings plus relevant working/episodic memory and maintains candidate hypotheses. Confidence should depend on persistence, independent sources, deviation from baseline, evidence specificity, temporal consistency and contradictions. We do not want to hard-code scenario-specific weights before testing.

The synthesized state is handed to an **Action/Eligibility layer**. A deterministic **Guardrail/Compliance layer** checks whether the proposed action is allowed and whether human review is required. Sensitive, high-impact, ambiguous or unresolved decisions go through a real **HITL checkpoint**, where a reviewer can approve, reject or modify the proposal.

### Memory and traceability

We currently separate memory into: raw immutable events; short-term working state; per-customer episodic memory; and shared semantic/policy knowledge. Structured customer state is scoped by `customer_id` to reduce cross-customer leakage.

Every final output should be traceable back through evidence event IDs, feature/baseline updates, specialist findings, synthesis, guardrail checks and HITL. This also gives us an actual "why" path rather than generating explanations after the decision.

### Research that informed the direction

We reviewed the PS architecture guidance together with Apache Flink material on event time/watermarks, AutoGen material on swarm/handoff coordination, and OpenAI Agents SDK documentation on specialized agents, handoffs, guardrails and tracing. The strongest change from this reading was moving away from "one LLM + full customer history" toward **event-time-aware streaming + structured specialist findings + shared state + explicit policy/HITL boundaries**.

### Immediate implementation plan

The next implementation milestone is:

`schema parser and replay → event-time/deduplication layer → historical baselines → state board → four specialist agents → synthesis/confidence → bounded action mapping → deterministic guardrails/HITL → required inferred-events output → trace/evaluation harness`

At mid-term, the architecture is intentionally preliminary. We expect confidence calibration, memory retrieval/decay and disagreement arbitration to change after testing. The aim is to preserve the core contracts while iterating on the internal reasoning method.
