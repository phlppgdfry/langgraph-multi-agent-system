"""LangSmith utilities: automated feedback logging, dataset creation, and prompt management."""

import os

from dotenv import load_dotenv

load_dotenv()


def get_langsmith_client():
    """Retrieve an authenticated LangSmith client if configured."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return None

    try:
        from langsmith import Client

        endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://eu.api.smith.langchain.com")
        return Client(api_url=endpoint, api_key=api_key)
    except Exception:  # noqa: BLE001
        return None


def log_critic_feedback(
    run_id: str,
    score: float,
    comment: str = "Verified by Critic reflection agent",
    key: str = "critic_rigor_score",
) -> bool:
    """Push critic quality score directly to the LangSmith Feedback column for a run.

    Args:
        run_id: The UUID string of the LangSmith root run.
        score: Normalized score between 0.0 and 1.0 (or 0-100).
        comment: Feedback rationale or justification.
        key: The feedback metric name.

    Returns:
        True if feedback was successfully created, False otherwise.
    """
    client = get_langsmith_client()
    if not client or not run_id:
        return False

    try:
        norm_score = float(score) / 100.0 if score > 1.0 else float(score)
        client.create_feedback(
            run_id=run_id,
            key=key,
            score=norm_score,
            comment=comment,
        )
        return True
    except Exception:  # noqa: BLE001
        return False


def sync_langsmith_benchmark_dataset(dataset_name: str = "nexus-benchmark-dataset") -> str | None:
    """Create or update a benchmark dataset in LangSmith's 'Datasets & Experiments' tab.

    This populates the Datasets & Experiments section visible in the user's LangSmith menu.
    """
    client = get_langsmith_client()
    if not client:
        return None

    benchmark_examples = [
        {
            "inputs": {"task": "Analyze Enterprise Multi-Agent LangGraph Swarms in 2026"},
            "outputs": {
                "expected_gain": "+42% accuracy",
                "min_score": 85,
                "required_topics": ["StateGraph", "LangSmith", "reflection"],
            },
        },
        {
            "inputs": {"task": "Autonomous AI Agent Swarms in Global Supply Chain Operations"},
            "outputs": {
                "expected_gain": "34% dwell time reduction",
                "min_score": 80,
                "required_topics": ["demurrage", "exception handling", "governance"],
            },
        },
        {
            "inputs": {"task": "Enterprise FinOps for Autonomous AI Agents and Token Budgets"},
            "outputs": {
                "expected_gain": "+37.5% cost reduction",
                "min_score": 80,
                "required_topics": ["token budgeting", "caching", "routing"],
            },
        },
    ]

    try:
        # Check if dataset already exists
        datasets = list(client.list_datasets(dataset_name=dataset_name))
        if datasets:
            dataset = datasets[0]
        else:
            dataset = client.create_dataset(
                dataset_name=dataset_name,
                description="Core evaluation benchmark suite for Nexus LangGraph Multi-Agent Swarm.",
            )

        # Upload examples if empty
        existing_examples = list(client.list_examples(dataset_id=dataset.id))
        if not existing_examples:
            for ex in benchmark_examples:
                client.create_example(
                    inputs=ex["inputs"],
                    outputs=ex["outputs"],
                    dataset_id=dataset.id,
                )

        return dataset.id
    except Exception:  # noqa: BLE001
        return None
