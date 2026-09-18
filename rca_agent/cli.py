import argparse,json
from .agent import RCAAgent
from .gateway import ReadOnlyGateway
def main():
    p=argparse.ArgumentParser();p.add_argument("--incident",required=True);p.add_argument("--namespace",default="rca-demo");p.add_argument("--json",action="store_true")
    a=p.parse_args();r=RCAAgent(ReadOnlyGateway(a.namespace)).investigate(a.incident)
    print(json.dumps(r,indent=2) if a.json else f"\n=== KUBERNETES RCA ===\nIncident: {r['incident']}\nRoot cause: {r['root_cause']}\nConfidence: {r['confidence']}\nEvidence items: {len(r['evidence'])}")
if __name__=="__main__":main()
