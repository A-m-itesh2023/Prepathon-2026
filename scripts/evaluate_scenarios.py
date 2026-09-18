import argparse
from rca_agent.agent import RCAAgent
from rca_agent.gateway import ReadOnlyGateway

SCENARIOS = [
    ("OOM", "checkout pods are restarting after memory pressure"),
    ("BAD_DEPLOYMENT", "checkout has a sudden increase in 5xx errors after a deployment"),
    ("DEPENDENCY", "checkout is failing because its database dependency is unavailable"),
    ("CONFIG", "checkout degraded after a configuration change"),
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--namespace", default="rca-demo")
    args = p.parse_args()
    agent = RCAAgent(ReadOnlyGateway(args.namespace))
    for name, incident in SCENARIOS:
        r = agent.investigate(incident)
        print(f"\n[{name}] {r['root_cause']} (confidence={r['confidence']})")
        print("queries:", ", ".join(e["query"] for e in r["evidence"]))

if __name__ == "__main__":
    main()
