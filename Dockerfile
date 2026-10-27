# Multi-stage container build for Nexus LangGraph Swarm
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project definition and lockfile
COPY pyproject.toml uv.lock ./

# Install python dependencies
RUN uv sync --frozen --no-dev

# Copy application source code
COPY . .

# Expose Streamlit dashboard port
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default launch command: Streamlit UI
CMD ["uv", "run", "streamlit", "run", "src/langgraph_multi_agent_system/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
