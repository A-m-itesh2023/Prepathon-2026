from .models import Hypothesis
class InvestigationReasoner:
    def initial_hypotheses(self,incident):
        return [Hypothesis("application defect"),Hypothesis("bad deployment"),Hypothesis("dependency failure"),Hypothesis("resource exhaustion"),Hypothesis("configuration problem")]
    def next_query(self,state):
        sources={e.source for e in state.evidence}; text=state.incident.lower()
        if "kubernetes" not in sources:return "pods"
        if "events" not in sources:return "events"
        if "deployments" not in sources:return "deployments"
        if "logs" not in sources:return "logs"
        if ("5xx" in text or "error" in text or "latency" in text) and "prometheus" not in sources:return "metrics"
        return None
    def update(self,state):
        blob="\n".join(str(e.observation) for e in state.evidence).lower()
        for h in state.hypotheses.values():h.score*=0.9
        if "oomkilled" in blob or "outofmemory" in blob:
            state.hypotheses["resource exhaustion"].score+=5;state.hypotheses["resource exhaustion"].supporting.append("Observed OOM/resource exhaustion evidence")
        if "deployment" in blob and ("5xx" in blob or "error" in blob or "crash" in blob):
            state.hypotheses["bad deployment"].score+=3;state.hypotheses["bad deployment"].supporting.append("Deployment and application-failure evidence co-occur")
        if "connection refused" in blob or "database unavailable" in blob or "dependency" in blob:
            state.hypotheses["dependency failure"].score+=4;state.hypotheses["dependency failure"].supporting.append("Dependency failure evidence observed")
        if "config" in blob or "configuration" in blob:
            state.hypotheses["configuration problem"].score+=2;state.hypotheses["configuration problem"].supporting.append("Configuration-related evidence observed")
