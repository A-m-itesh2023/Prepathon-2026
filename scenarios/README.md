# Reproducible incidents

Each directory contains a workload with a documented ground-truth failure mode. Apply the base namespace first, then apply an individual scenario:

```bash
kubectl apply -f scenarios/base/
kubectl apply -f scenarios/oom/workload.yaml
```

Use the same pattern for `bad-deployment`, `dependency-failure`, and `config-drift`. The scenarios are deliberately small so the causal chain can be inspected with Kubernetes resources, Events and logs.
