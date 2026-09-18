import pytest
from rca_agent.gateway import ReadOnlyGateway

def test_command_capability_is_not_available():
    with pytest.raises(PermissionError):
        ReadOnlyGateway._deny_untrusted_command("rm -rf /")

def test_unknown_query_rejected():
    from rca_agent.agent import RCAAgent
    agent = RCAAgent(ReadOnlyGateway("rca-demo"))
    with pytest.raises(ValueError):
        agent._execute("exec")
