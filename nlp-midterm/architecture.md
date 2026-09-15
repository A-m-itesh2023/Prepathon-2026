# Preliminary System Architecture

## Agentic Customer 360 — Proactive Intervention Desk

**Participant:** Amitesh Mitra  
**Roll No.:** 26055002  
**Branch:** Industrial Chemistry  
**Stage:** Mid-term

## 1. Design goal

The architecture is designed around one central idea: **customer state should be built from evidence over time, not inferred from isolated events**.

The system should continuously process the event stream, compare current behaviour with the customer's historical baseline, combine evidence from specialist agents, maintain candidate hypotheses, and only then choose a bounded action.

## 2. High-level flow

```text
                    ┌──────────────────────────┐
                    │   History + Live Events   │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Event-time Ingestion      │
                    │ ordering / dedup / late  │
                    │ event reconciliation     │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       Transaction Agent   Usage Agent       Support Agent
              │                  │                  │
              └────────────┬─────┴──────┬───────────┘
                           ▼            ▼
                    KYC/Profile Agent  
                           │
                           ▼
                ┌──────────────────────┐
                │ Customer State Board │◄──── Memory / Retrieval
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Synthesis /          │
                │ Life-Event Inference │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Action / Eligibility │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Guardrail / Critic   │
                └──────────┬───────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                  HITL          Auto path
                    │             │
                    └──────┬──────┘
                           ▼
                Fixed output + audit trace
```

## 3. Event-time ingestion

The supplied stream contains both `event_time` and `ingestion_time`, and late/out-of-order events are expected. Therefore the ingestion layer should not treat arrival order as the source of truth.

For the prototype:

1. load `history_seed.jsonl` first;
2. establish historical features/baselines;
3. read live events;
4. buffer/reorder using `event_time` within a bounded lateness window;
5. deduplicate using `event_id`;
6. update affected customer state when a late event changes a derived feature.

The implementation should retain the original timestamps so that a final explanation can distinguish when something happened from when it was received.

## 4. Specialist agents

The current decomposition uses four source-focused specialists.

### Transaction/Billing Agent

**Inputs:** card payments, transfers, ledger events and relevant account history.

**Produces:** spending changes, income changes, cash-flow anomalies, recurring-payment changes and transaction-level context.

### Usage/Engagement Agent

**Inputs:** web/app activity and historical engagement features.

**Produces:** login-frequency changes, feature-use changes, session trends and signs of declining/increasing engagement.

### Support/Sentiment Agent

**Inputs:** support tickets, transcripts and resolution outcomes.

**Produces:** issue type, sentiment/urgency signals, explicit intent and whether another transaction or hypothesis was explained by the support interaction.

### KYC/Profile Agent

**Inputs:** KYC/profile changes.

**Produces:** structured changes such as dependents, marital/relationship status, address and other profile signals relevant to life-event inference.

Each specialist should return a typed `SignalFinding`, approximately:

```json
{
  "customer_id": "...",
  "signal_type": "...",
  "summary": "...",
  "evidence_event_ids": ["..."],
  "event_time_start": "...",
  "event_time_end": "...",
  "confidence": "low|medium|high",
  "source_agent": "...",
  "trace_id": "..."
}
```

The exact schema can be refined during implementation.

## 5. Customer State Board

The state board is the main coordination contract between agents. It is scoped per customer and stores structured state rather than unrestricted model context.

Example shape:

```json
{
  "customer_id": "...",
  "baseline_summary": {},
  "rolling_features": {},
  "active_findings": [],
  "candidate_hypotheses": [],
  "current_inferred_state": "...",
  "confidence_band": "low|medium|high",
  "supporting_evidence": [],
  "contradicting_evidence": [],
  "recent_actions": [],
  "open_cases": [],
  "last_updated_trace_id": "..."
}
```

Agents do not receive another agent's hidden chain-of-thought. They receive only structured findings and permitted evidence. Customer ID is enforced at the data layer to reduce memory bleed.

## 6. Memory model

**Working memory:** recent events, rolling features, open hypotheses and current case context.

**Episodic memory:** compact customer-specific summaries of past significant events/interventions/outcomes.

**Semantic/policy memory:** shared rules, action eligibility, compliance constraints and general patterns.

**Raw event store:** immutable source of truth for evidence citations and replay.

Retrieval is selective: synthesis asks for relevant memories by customer + time + topic rather than injecting the full history into every prompt.

## 7. Synthesis and confidence

The synthesis stage maintains more than one candidate hypothesis when needed.

Preliminary confidence logic is based on:

- number of independent source systems;
- persistence over time;
- deviation from historical baseline;
- specificity of evidence;
- temporal coherence;
- explicit contradictory/explanatory evidence;
- recency.

Example: one unusual purchase may create a weak hypothesis. A matching intent search plus KYC change can strengthen it. A support transcript explaining the purchase can reduce a fraud hypothesis.

The exact numeric calibration is deliberately not fixed at mid-term because it should be tested against practice scenarios without overfitting them.

## 8. Decision and action policy

The synthesis layer returns a candidate `inferred_state` and confidence. The Action/Eligibility Agent then chooses only from the allowed action enum.

A deterministic policy layer can enforce rules such as:

- low confidence → prefer `no_action` or HITL;
- sensitive/high-impact action → HITL required;
- unresolved agent disagreement → HITL;
- ineligible offer → block `personalized_offer`;
- fraud/compliance hold cannot be executed solely because an LLM suggested it.

**The model proposes; policy authorizes.**

## 9. HITL

The HITL checkpoint is an actual interruption, not a log message. The reviewer sees:

- proposed state/action;
- confidence;
- supporting and contradicting evidence;
- short evidence-backed explanation;
- relevant policy result.

The human can **approve, reject or modify**. The exact context shown and the decision are appended to the audit log.

## 10. Observability / traceability

Each incoming event and derived decision gets a trace path:

`event → feature update → specialist finding → state-board update → synthesis → action proposal → guardrail → HITL → final output`

Log at minimum:

- trace ID;
- agent invocation;
- tool/data query;
- event IDs retrieved;
- handoff input/output;
- confidence;
- guardrail result;
- HITL decision;
- event-time-to-decision latency.

This provides a reproducible explanation instead of asking the model to invent an explanation after the action.

## 11. Synchronous vs asynchronous paths

**Asynchronous/background:** normal ingestion, feature updates, engagement rollups, memory compaction, slow life-event inference.

**Immediate/event-driven:** support escalation signals, high-risk guardrail patterns and any path that requires a timely compliance/fraud decision.

Both paths update the same customer-scoped state board.

## 12. Why this architecture fits the three practice scenarios

The architecture is intentionally scenario-agnostic:

- **Scenario 1** needs historical income baseline + healthcare transactions + search/support correlation + late-event correctness.
- **Scenario 2** needs gradual multi-source evidence accumulation and contradiction of a false fraud hypothesis.
- **Scenario 3** needs longitudinal engagement/relationship trends and early churn detection despite a misleading positive balance event.

The common solution is not a scenario-specific rule tree. It is **event-time-aware evidence accumulation over a customer baseline with specialized interpretation, shared state, contradiction handling and bounded action policy**.

## 13. Prototype stack under consideration

- Python for replay, feature extraction and evaluation.
- Pydantic/JSON Schema for typed event and agent contracts.
- Lightweight local store (SQLite/Postgres) for events/state during prototype.
- Optional vector retrieval only for unstructured episodic/policy text; structured financial features remain in structured storage.
- Agent orchestration via a framework supporting tools, handoffs, guardrails and tracing, or a small custom orchestrator if framework overhead becomes limiting.
- Minimal CLI/table-based HITL rather than spending time on frontend polish.

Framework choice is still provisional; the architectural contracts are intended to remain stable even if the orchestration library changes.
