from .models import Evidence, InvestigationState
from .reasoner import InvestigationReasoner
class RCAAgent:
    def __init__(self,gateway,max_iterations=8):
        self.gateway=gateway;self.reasoner=InvestigationReasoner();self.max_iterations=max_iterations
    def investigate(self,incident):
        state=InvestigationState(incident=incident,namespace=self.gateway.namespace)
        for h in self.reasoner.initial_hypotheses(incident):state.hypotheses[h.name]=h
        for _ in range(self.max_iterations):
            state.iterations+=1;query=self.reasoner.next_query(state)
            if not query:break
            state.queries.append(query);result=self._execute(query)
            state.evidence.append(Evidence(result.source,result.query,self._safe_text(result.data)))
            state.timeline.append(f"iteration {state.iterations}: {result.source} -> {result.query}")
            self.reasoner.update(state)
        ranked=sorted(state.hypotheses.values(),key=lambda x:x.score,reverse=True);top=ranked[0] if ranked else None
        confidence=self._confidence(top.score if top else 0,len(state.evidence))
        if not top or top.score<=0:conclusion="Insufficient evidence to identify a defensible root cause.";confidence="low"
        else:conclusion=top.name
        return {"incident":incident,"root_cause":conclusion,"confidence":confidence,"iterations":state.iterations,
                "observed_facts":[e.observation for e in state.evidence],"evidence":[e.__dict__ for e in state.evidence],
                "hypotheses":[h.__dict__ for h in ranked],"timeline":state.timeline,
                "alternative_explanations":[h.name for h in ranked[1:3]],"uncertainty":state.uncertainty}
    def _execute(self,query):
        if query=="pods":return self.gateway.pods()
        if query=="events":return self.gateway.events()
        if query=="deployments":return self.gateway.deployments()
        if query=="logs":
            pods=self.gateway.pods().data;return self.gateway.logs(pods[0]["name"] if isinstance(pods,list) and pods else "unknown")
        if query=="metrics":return self.gateway.metrics("http://prometheus.monitoring.svc:9090","up")
        raise ValueError("Unallow-listed investigation query")
    @staticmethod
    def _safe_text(value):return value if isinstance(value,str) else str(value)
    @staticmethod
    def _confidence(score,evidence_count):
        if score>=5 and evidence_count>=3:return "high"
        if score>=2:return "medium"
        return "low"
