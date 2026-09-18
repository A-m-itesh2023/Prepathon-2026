"""Read-only observability gateway. No generic shell/exec primitive is exposed."""
from dataclasses import dataclass
import json

try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

@dataclass
class ToolResult:
    source: str
    query: str
    data: object

class ReadOnlyGateway:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self._k8s = None
        if client and config:
            try:
                config.load_kube_config()
            except Exception:
                try:
                    config.load_incluster_config()
                except Exception:
                    pass
            self._k8s = {"core": client.CoreV1Api(), "apps": client.AppsV1Api()}

    @staticmethod
    def _deny_untrusted_command(*_args, **_kwargs):
        raise PermissionError("Command execution is outside the RCA agent capability boundary")

    def pods(self):
        if not self._k8s:
            return ToolResult("kubernetes", "list pods", "Kubernetes client unavailable")
        items = self._k8s["core"].list_namespaced_pod(self.namespace).items
        rows = []
        for p in items:
            rows.append({
                "name": p.metadata.name,
                "phase": p.status.phase,
                "restarts": sum((c.restart_count or 0) for c in (p.status.container_statuses or [])),
                "reason": next((c.state.waiting.reason for c in (p.status.container_statuses or [])
                                if c.state and c.state.waiting), None),
            })
        return ToolResult("kubernetes", "list pods", rows)

    def deployments(self):
        if not self._k8s:
            return ToolResult("kubernetes", "list deployments", "Kubernetes client unavailable")
        items = self._k8s["apps"].list_namespaced_deployment(self.namespace).items
        return ToolResult("kubernetes", "list deployments", [
            {"name": d.metadata.name, "replicas": d.spec.replicas,
             "updated": d.status.updated_replicas, "available": d.status.available_replicas,
             "image": d.spec.template.spec.containers[0].image if d.spec.template.spec.containers else None}
            for d in items
        ])

    def events(self):
        if not self._k8s:
            return ToolResult("events", "list events", "Kubernetes client unavailable")
        items = self._k8s["core"].list_namespaced_event(self.namespace).items
        return ToolResult("events", "list events", [
            {"reason": e.reason, "type": e.type, "message": e.message,
             "object": getattr(e.involved_object, "name", None),
             "time": str(e.last_timestamp or e.event_time or e.first_timestamp)}
            for e in items
        ])

    def logs(self, pod, container=None, tail_lines=200):
        if not self._k8s:
            return ToolResult("logs", f"logs {pod}", "Kubernetes client unavailable")
        text = self._k8s["core"].read_namespaced_pod_log(
            name=pod, namespace=self.namespace, container=container, tail_lines=tail_lines
        )
        return ToolResult("logs", f"logs {pod}", text)

    def metrics(self, prometheus_url, query):
        import urllib.parse, urllib.request
        url = prometheus_url.rstrip("/") + "/api/v1/query?" + urllib.parse.urlencode({"query": query})
        with urllib.request.urlopen(url, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
        return ToolResult("prometheus", query, body)
