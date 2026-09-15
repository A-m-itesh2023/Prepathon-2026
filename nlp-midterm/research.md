# NLP Mid-Term Research Log

## Agentic Customer 360 — Proactive Intervention Desk

**Participant:** Amitesh Mitra  
**Roll No.:** 26055002  
**Branch:** Industrial Chemistry  
**Status:** Mid-term progress submission  
**Date:** 15 September 2026

## 1. Problem understanding

The problem is not to build a chatbot or a dashboard. The target is an **ambient, event-driven Customer 360 system** that continuously observes heterogeneous customer events, maintains an evolving customer state, correlates weak signals across sources, and commits to a bounded decision: an inferred customer state, confidence band, action (including explicit `no_action`), and HITL status.

The supplied dataset makes three constraints especially important:

1. `history_seed.jsonl` is needed to establish a customer's normal baseline before the live window.
2. Decisions should follow **event time**, not simply ingestion order, because events can be late or out of order.
3. A single unusual event is often insufficient. The useful signal is usually a **cross-source pattern over time**, and misleading/red-herring events must not cause premature action.

## 2. Dataset exploration completed

We inspected the common schema and the three supplied practice scenarios. The common event envelope contains:

`event_id, event_time, ingestion_time, customer_id, account_id, source_system, event_type, schema_version, payload`

The source systems include card payments, bank ledger events, transfers, KYC changes, web/app activity, support logs, brokerage activity and consented social signals. This suggests that source-specific interpretation should happen before global synthesis rather than sending every raw event directly to one general-purpose LLM.

### Scenario 1 observations — financial/medical stress pattern

The historical stream establishes a stable salary baseline of about **$3,800 every two weeks**. In the live stream we observed:

- healthcare/ER spend followed by pharmacy spend;
- salary later being replaced by lower benefit-like credits;
- a large hospital bill;
- a late-arriving healthcare event, showing why event-time handling matters;
- a large internal transfer that should not automatically be interpreted as net wealth loss;
- a web search for a medical hardship plan;
- an explicit support request mentioning hospitalization, reduced income and a payment plan.

There are also isolated large transfers/refunds that could distract a naive anomaly detector. The architectural lesson is that **magnitude is not meaning**: transaction anomalies need counterparty/category/context and cross-source evidence.

### Scenario 2 observations — gradual life-event inference

The historical salary baseline is **$4,500**, while the live salary credits drop to **$2,700**. The live stream also contains:

- baby-product spending;
- a support interaction clarifying that a large electronics purchase was a baby monitor;
- a search for a child education savings plan;
- a recurring daycare standing instruction;
- a KYC `dependents_change` from 1 to 2.

No single early signal proves the life event. Confidence should accumulate as independent evidence appears. The support clarification is also important: an apparently suspicious high-value purchase can be explained by another source, so the system needs a mechanism for **evidence that cancels or weakens another agent's hypothesis**.

### Scenario 3 observations — slow churn pattern

The customer has a long-tenure, high-value profile and a historical salary baseline of **$5,000**. The live stream shows:

- a complaint about an international transaction fee;
- the request being rejected;
- later cancellation of standing instructions;
- reduced digital engagement;
- movement of money away from the primary banking relationship;
- eventually behavior consistent with the account becoming less central.

A large tax refund temporarily increases the balance and could be mistaken for a wealth-growth opportunity. The broader trajectory is more important than the point-in-time balance. This scenario therefore emphasizes **trend memory and early detection**.

## 3. Cross-scenario findings

Across all three scenarios, we found the same recurring reasoning problem:

**raw event → source-specific signal → baseline comparison → shared customer state → competing hypotheses → synthesis → action policy → HITL/guardrail → auditable output**

This is why our preliminary design is a hybrid multi-agent system rather than one LLM receiving the entire raw stream.

The three scenarios also suggest four confidence principles:

- **Persistence:** repeated or sustained changes matter more than one-off events.
- **Independence:** evidence from different source systems should raise confidence more than repeated evidence from one source.
- **Specificity:** explicit KYC/support/intent evidence should generally carry more weight than a generic spend anomaly.
- **Contradiction:** contextual evidence can reduce confidence and prevent false positives.

We are treating these as design principles rather than fixed numeric weights at this stage.

## 4. Research trail and what it changed

### A. Problem statement: Agentic Customer 360 — Proactive Intervention Desk

**Source:** supplied NLP problem statement.

**Takeaway:** The PS explicitly separates working, episodic and semantic/shared memory; recommends a shared per-customer state board; discusses swarm, handoff, debate, round-robin and critique-refiner coordination; and requires real HITL, guardrails, observability, traceability and explainability.

**Design impact:** We use parallel source specialists for signal extraction, then a centralized synthesis/correlation stage. We do not share unrestricted agent chain-of-thought; agents publish structured findings to a customer-scoped state board.

### B. Apache Flink — Timely Stream Processing / Event Time and Watermarks

**Link:** https://nightlies.apache.org/flink/flink-docs-master/docs/concepts/time/

**Takeaway:** Event time represents when an event actually happened, while watermarks provide a practical way to make progress despite out-of-order arrivals.

**Design impact:** Our ingestion layer is event-time aware. For the prepathon prototype we can replay and reorder/buffer by `event_time`; for a production version we would use bounded-lateness/watermark logic rather than assuming arrival order is correct.

### C. Apache Flink — Generating Watermarks

**Link:** https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/

**Takeaway:** Bounded-out-of-orderness strategies allow a stream processor to tolerate late records while still advancing windows.

**Design impact:** Windowed features such as login-frequency trends, transaction volume and rolling baselines should be recomputable when a late event falls inside an active lateness window. We should also deduplicate by `event_id`.

### D. Microsoft AutoGen — Swarm

**Link:** https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html

**Takeaway:** Specialist agents can delegate/handoff based on capability, but shared context can become broad and difficult to control.

**Design impact:** We borrow the specialization idea but prefer a **structured state board** over broadcasting the full conversation/context to every specialist.

### E. Microsoft AutoGen — Handoff Design Pattern

**Link:** https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/design-patterns/handoffs.html

**Takeaway:** Event-driven agents can delegate a scoped task to another specialist, and handoffs are useful when responsibility genuinely changes.

**Design impact:** Our flow uses explicit typed handoffs: source agents publish `SignalFinding`; the Synthesis Agent publishes `CustomerHypothesis`; the Action layer receives only the synthesized state plus supporting evidence IDs.

### F. OpenAI Agents SDK — Agents, Handoffs, Guardrails and Tracing

**Links:**  
https://openai.github.io/openai-agents-python/  
https://openai.github.io/openai-agents-python/handoffs/  
https://openai.github.io/openai-agents-python/guardrails/  
https://openai.github.io/openai-agents-python/tracing/

**Takeaway:** The SDK exposes agents with specialized tools, handoffs, validation/guardrails and end-to-end traces covering model generations, tools, handoffs and guardrails.

**Design impact:** This is a practical candidate for the prototype orchestration layer. Regardless of framework choice, we want the same properties: typed tool boundaries, explicit handoffs, hard guardrails around side effects, and a trace ID linking each final decision back to the evidence and agent/tool activity that produced it.

## 5. Preliminary memory design

We currently plan four layers:

1. **Raw event store** — immutable event records keyed by customer and event ID.
2. **Working state** — recent event-time window, active hypotheses, open support cases, rolling features.
3. **Episodic memory** — compact per-customer summaries of important past events, interventions and outcomes.
4. **Semantic/policy store** — action eligibility, compliance rules and general domain knowledge shared across customers.

A separate **Customer State Board** is the contract between agents. It contains structured findings, not free-form hidden reasoning. Every entry carries `customer_id`, evidence event IDs, event-time range, confidence, source agent and trace ID.

This design is intended to reduce context pollution, prevent cross-customer memory leakage, and make explanations reproducible.

## 6. Preliminary MAS coordination

### Parallel signal layer

- Transaction/Billing Agent
- Usage/Engagement Agent
- Support/Sentiment Agent
- KYC/Profile Agent

Each agent sees only the data/tools required for its domain and emits a common `SignalFinding` schema.

### Correlation layer

A Synthesis/Life-Event Agent reads the structured findings and relevant memory. It maintains candidate hypotheses rather than forcing an early single label.

### Arbitration / critique

A Critique/Compliance-Refiner checks whether the proposed state and action are supported, whether there is contradictory evidence, and whether a guardrail/HITL condition is triggered.

### Action layer

An Action/Eligibility component maps the final state to the fixed action enum. It does not invent new side effects.

## 7. Guardrails, HITL and explainability

The PS requires actual guardrails, observability, traceability and explainability. Our current approach is:

- keep customer data access scoped to `customer_id`;
- validate agent outputs against typed schemas;
- separate model recommendations from deterministic policy authorization;
- require human review for sensitive/high-impact or unresolved decisions;
- record supporting and contradicting evidence IDs;
- preserve a trace from final output back to the events and agent steps that produced it.

The intended explanation is evidence-based: **what changed, which events support it, what competing interpretation was considered, and why the chosen action was allowed**.

## 8. Implementation plan

The first implementation milestone is deliberately small:

1. parse the supplied schema;
2. load the history seed;
3. establish customer baselines;
4. replay the live stream using event time;
5. deduplicate and handle late events;
6. maintain the state board;
7. add specialist agents with structured outputs;
8. add synthesis and confidence updates;
9. add action mapping, guardrails and HITL;
10. build a trace/evaluation harness around the fixed output schema.

## 9. Open questions for implementation

The main areas I still want to validate experimentally are:

- how much of the feature extraction should be deterministic versus LLM-based;
- what memory should expire and what should persist;
- how to calibrate confidence without overfitting the supplied scenarios;
- how to arbitrate conflicting specialist findings;
- how much retrieval context is useful before it becomes noise;
- what latency trade-offs are acceptable for background versus immediate triggers.

These are intentionally left open at mid-term rather than being presented as solved problems.
