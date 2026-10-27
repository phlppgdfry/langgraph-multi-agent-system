# Contributing to Nexus Multi-Agent Swarm

We welcome contributions to Nexus! Follow these guidelines to maintain production-grade standards.

---

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/phlppgdfry/langgraph-multi-agent-system.git
   cd langgraph-multi-agent-system
   ```

2. **Sync dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Or run the configuration wizard:
   uv run python -m langgraph_multi_agent_system.cli --configure
   ```

---

## 🧪 Testing & Quality Standards

Before opening a pull request, ensure all tests and linter checks pass:

1. **Run full pytest suite:**
   ```bash
   uv run pytest -v
   ```

2. **Run Ruff code linter & formatter:**
   ```bash
   uv run ruff check .
   ```

3. **Verify benchmark evaluations:**
   ```bash
   uv run python -m langgraph_multi_agent_system.cli --evals
   ```

---

## 🌿 Branching & Commit Conventions

- Use feature branches: `feat/feature-name` or `fix/bug-fix`.
- Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `style:`, `test:`.
- Ensure all GitHub Actions workflows pass (`CI` & `Deploy GitHub Pages`).
