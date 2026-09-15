# Agentic Customer 360 — Mid-Term Submission

**Problem Statement:** Agentic Customer 360 — Proactive Intervention Desk  
**Participant:** Amitesh Mitra  
**Roll No.:** 26055002  
**Branch:** Industrial Chemistry  
**Submission:** Mid-Term

## What this repository contains

This repository is a snapshot of my progress on the NLP problem statement up to the mid-term submission. The main focus so far has been understanding the event-stream data properly, studying the problem requirements, and turning those findings into a practical system architecture.

I have intentionally kept this as a **mid-term snapshot rather than presenting it as a finished system**. The architecture is still open to changes as implementation starts and more experiments are done.

## Work completed so far

### 1. Understood the data and event stream

I went through the supplied schema and the history/live streams and looked at how different customer signals appear across sources such as:

- card payments and refunds
- banking/ledger events
- web and app activity
- support interactions
- KYC/customer-profile changes
- transfers and recurring payments

A key observation was that the system cannot simply look at one event at a time. Event time matters, events can arrive late/out of order, and useful signals often appear only after combining multiple sources.

### 2. Studied the three scenarios

I traced the supplied scenarios to understand what kinds of evidence the final system will need to combine.

Some examples include:

- medical-related transactions + reduced income + a hardship search/support request
- baby-related purchases + daycare activity + a later KYC dependent change
- support friction + reduced engagement + account activity that can indicate churn risk

I also noted the importance of **red herrings and contradictory signals**, since a single unusual transaction should not automatically become a life-event prediction.

### 3. Explored the multi-agent approach

The current direction is a hybrid multi-agent architecture rather than one large agent trying to interpret everything.

The preliminary design separates source-specific analysis from cross-source reasoning. Specialist agents produce structured signals, which are then combined by a synthesis/life-event layer before an action decision is made.

### 4. Thought through memory and traceability

I am treating memory as more than just a vector database. The current design separates:

- raw event history
- short-term working context
- episodic customer history
- semantic/policy knowledge
- a current customer state board

The goal is to make it possible to answer not only **"what did the system decide?"** but also **"what evidence caused the decision?"**.

### 5. Looked at event-time processing and agent coordination

I reviewed material around event-time/watermark based stream processing and multi-agent handoff/coordination patterns. These readings helped shape the current ideas around late events, scoped agent handoffs, parallel specialist analysis, synthesis, and traceability.

## Current architecture direction

```text
Incoming event stream
        ↓
Event-time ingestion + ordering
        ↓
Source-specific specialist agents
        ↓
Customer State Board + memory
        ↓
Cross-source synthesis / life-event inference
        ↓
Confidence + action/eligibility decision
        ↓
Guardrail / critic
        ↓
HITL when required
        ↓
Fixed evaluation output + audit trail
```

The detailed version is in [`architecture.md`](architecture.md), along with the proposed agent responsibilities, memory design, synchronous/asynchronous parts, and observability approach.

## Repository files

| File | Purpose |
|---|---|
| [`research.md`](research.md) | Research trail, dataset observations, scenario analysis, and design findings |
| [`architecture.md`](architecture.md) | Preliminary system architecture and component responsibilities |
| [`midterm_report.md`](midterm_report.md) | Short mid-term summary of findings and intended implementation direction |
| [`system_architecture.png`](system_architecture.png) | Visual overview of the proposed architecture |

## What I plan to do next

The next step is to move from the architecture into a working prototype. The initial implementation will focus on getting the event stream and customer state handling correct before adding more sophisticated agent behaviour.

Planned steps are:

1. Build the event-time ingestion/replay layer.
2. Create structured outputs for the specialist agents.
3. Maintain and update the customer state board.
4. Implement cross-source synthesis and confidence updates.
5. Add action selection, guardrails and the HITL checkpoint.
6. Add tracing/audit information so each final decision has a clear evidence path.
7. Test the approach across the supplied scenarios, including late events and misleading signals.

## Mid-term status

**Self-assessed completion: 2/5**

This reflects that the research, dataset understanding and preliminary architecture are in place, while the end-to-end implementation is still to be built and tested.

---

*This repository is intended to document the work done so far for the mid-term checkpoint. The design may evolve as implementation and testing reveal better approaches.*
