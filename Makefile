.PHONY: help install run ui test lint format evals sync-langsmith docker-build docker-up clean

PYTHON := uv run python
PYTEST := uv run pytest
RUFF := uv run ruff
STREAMLIT := uv run streamlit

help: ## Show this help message
	@echo "Nexus Multi-Agent System - Command Shortcuts"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies via uv
	uv sync --all-groups

run: ## Execute the CLI multi-agent swarm pipeline
	$(PYTHON) -m langgraph_multi_agent_system.cli

ui: ## Launch the interactive Streamlit web dashboard
	$(STREAMLIT) run src/langgraph_multi_agent_system/app.py

test: ## Run full unit and integration test suite
	$(PYTEST) -v

lint: ## Check code formatting and static typing
	$(RUFF) check .
	$(RUFF) format --check .

format: ## Automatically fix and format all Python files
	$(RUFF) check --fix .
	$(RUFF) format .

evals: ## Run automated LangSmith evaluation suite
	$(PYTHON) -m langgraph_multi_agent_system.cli --evals

sync-langsmith: ## 1-Click sync of all LangSmith assets (datasets, queues, prompts, evals)
	$(PYTHON) -m langgraph_multi_agent_system.cli --sync-langsmith

docker-build: ## Build multi-architecture production Docker container
	docker build -t nexus-swarm:latest .

docker-up: ## Start swarm with Docker Compose
	docker-compose up -d

clean: ## Clean bytecode, cache files, and checkpoint sqlite test databases
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
