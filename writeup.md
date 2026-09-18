# Kubernetes RCA Agent — Prepathon 2026

**Amitesh Mitra**  
**Roll No.: 26055002**  
**Branch: Industrial Chemistry, IIT (BHU) Varanasi**

## Submission Summary

This project implements a sandboxed AI agent for investigating Kubernetes incidents and producing a defensible root-cause analysis (RCA). The agent is designed as an iterative investigation loop rather than a static log summarizer.

The prototype gathers evidence from Kubernetes resources/events, application logs, and metrics where available, maintains competing hypotheses, chooses follow-up queries based on evidence gaps, and produces an RCA that separates observed facts, hypotheses, supporting/contradicting evidence, conclusion, confidence, timeline, uncertainty, and alternative explanations.

## Architecture

Incident → Evidence Planner → Read-only Tool Gateway → Kubernetes / Logs / Metrics → Evidence Normalizer → Hypothesis Ledger → Investigation Loop → RCA Writer.

The tool gateway is deliberately read-only. The model never receives unrestricted shell access, cluster-admin credentials, or host access. Tool calls are allow-listed and arguments are validated before execution.

## Observability Sources

Configured sources:
- Kubernetes API resources and Events
- Application/container logs
- Prometheus metrics

The architecture is extensible to Grafana, Loki, Elasticsearch/Kibana, and Jaeger/Tempo through MCP or direct APIs, but the submission only claims sources actually configured in the runnable prototype.

## Investigation Loop

1. Parse the incident statement.
2. Establish initial observations from Kubernetes state and recent Events.
3. Generate competing hypotheses.
4. Select the next information source/query based on uncertainty.
5. Gather evidence.
6. Update hypothesis support and contradictions.
7. Build a causal timeline.
8. Stop when evidence is sufficient or explicitly report insufficient confidence.
9. Produce a structured RCA.

## Reproducible Incident Scenarios

The test suite contains ground-truth incidents built around:
1. OOM/resource exhaustion.
2. Bad deployment causing application failures.
3. Dependency/database failure requiring correlation across sources.
4. Configuration-induced degradation.

Each scenario is intended to expose different causal patterns rather than merely different error messages.

## Security / Sandboxing

The prototype treats Kubernetes resources, logs, traces and application responses as untrusted data. Retrieved text cannot issue instructions to the model. Investigation tools are read-only and scoped to the permitted namespace/resources.

Security tests include:
- attempted command execution outside the tool allow-list;
- malformed tool arguments;
- prompt-injection text embedded in logs;
- attempts to access secrets or host-level resources.

These requests are denied before execution.

## Evaluation

The evaluation records:
- root-cause identification against known ground truth;
- evidence coverage;
- whether the agent investigated multiple sources when required;
- hypothesis updates;
- unsupported-claim rate;
- confidence calibration;
- security boundary violations;
- reproducibility of incident setup.

## Design Rationale

The central design choice is to make investigation state explicit. The agent does not simply ask an LLM for an RCA from a large context dump. It progressively retrieves high-signal evidence and updates a hypothesis ledger. This keeps context focused and makes the final conclusion auditable.

## Known Limitations

The prototype is intentionally scoped to a local reproducible environment. It does not claim production-scale observability coverage, unrestricted cluster administration, or fully general causal inference. Distributed tracing and external-system correlation are extension points rather than silently claimed implemented features.

## Next Steps

Future iterations could add traces, historical incident retrieval, richer change correlation, an explicit causal graph, and stronger automated evaluation across a larger incident corpus.
