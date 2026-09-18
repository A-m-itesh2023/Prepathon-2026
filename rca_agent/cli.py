import argparse, json
from .agent import RCAAgent
from .gateway import ReadOnlyGateway

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--incident", required=True)
    p.add_argument("--namespace", default="rca-demo")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = RCAAgent(ReadOnlyGateway(args.namespace)).investigate(args.incident)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print("\n=== KUBERNETES RCA ===")
    print("Incident:", result["incident"])
    print("Root cause:", result["root_cause"])
    print("Confidence:", result["confidence"])
    print("\nEvidence:")
    for e in result["evidence"]:
        print(f"- [{e['source']}] {e['query']}: {e['observation']}")
    print("\nHypotheses:")
    for h in result["hypotheses"]:
        print(f"- {h['name']}: score={h['score']}")
    print("\nTimeline:")
    for t in result["timeline"]: print("-", t)
    print("\nAlternatives:", ", ".join(result["alternative_explanations"]))

if __name__ == "__main__": main()
