import json
from dataclasses import dataclass
from rca_agent.agent import RCAAgent

@dataclass
class Result:
    source: str
    query: str
    data: object

class MockGateway:
    def __init__(self, observations):
        self.namespace = "prepathon"
        self.observations = observations

    def pods(self):
        pod = next(k for k in self.observations if k == "list pods")
        name = next((k.split(" ", 1)[1] for k in self.observations if k.startswith("logs ")), "app")
        return Result("kubernetes", pod, [{"name": name, "observation": self.observations[pod]}])

    def events(self):
        return Result("events", "list events", self.observations["list events"])

    def deployments(self):
        return Result("kubernetes", "list deployments", self.observations["list deployments"])

    def logs(self, pod, container=None, tail_lines=200):
        key = f"logs {pod}"
        return Result("logs", key, self.observations[key])

    def metrics(self, prometheus_url, query):
        return Result("prometheus", query, "No anomalous metric required for this ground-truth case.")

def run_case(name, observations, expected):
    result = RCAAgent(MockGateway(observations)).investigate(name)
    assert result["root_cause"] == expected, result
    assert len(result["evidence"]) >= 4, result
    return {
        "incident": name,
        "expected": expected,
        "predicted": result["root_cause"],
        "confidence": result["confidence"],
        "iterations": result["iterations"],
        "evidence_sources": [e["source"] for e in result["evidence"]],
    }

def test_ground_truth_scenarios():
    cases = [
        ("OOM workload", {
            "list pods": "Pod worker phase Failed; container terminated: OOMKilled",
            "list events": "Killing container because of memory limit",
            "list deployments": "Deployment worker replicas=1 image=busybox",
            "logs worker": "process exceeded memory allocation",
        }, "resource exhaustion"),
        ("Bad deployment", {
            "list pods": "Pod web pending; image pull failure",
            "list events": "Failed to pull image does-not-exist-prepathon",
            "list deployments": "Deployment web image=nginx:does-not-exist-prepathon",
            "logs web": "ERROR container unavailable after deployment",
        }, "bad deployment"),
        ("Dependency failure", {
            "list pods": "Pod api running; database pod unavailable",
            "list events": "database dependency unavailable",
            "list deployments": "Deployment api replicas=1",
            "logs api": "ERROR database connection refused",
        }, "dependency failure"),
        ("Configuration drift", {
            "list pods": "Pod config-app CrashLoopBackOff",
            "list events": "configuration caused application exit",
            "list deployments": "Deployment config-app replicas=1",
            "logs config-app": "configuration APP_MODE invalid-mode",
        }, "configuration problem"),
    ]
    results = [run_case(*case) for case in cases]
    with open("validation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
