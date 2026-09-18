cluster:
	kind create cluster --name rca-lab

deploy:
	kubectl apply -f scenarios/base/

security:
	python -m pytest tests -q

run:
	python -m rca_agent.cli --incident "checkout has a sudden increase in 5xx errors" --namespace rca-demo
