"""Unit tests for LangSmith utilities and integration functions."""

from unittest.mock import MagicMock, patch

from langgraph_multi_agent_system.langsmith_utils import (
    _resolve_run_id,
    get_langsmith_client,
    get_or_create_annotation_queue,
    log_critic_feedback,
    push_all_prompts_to_hub,
    push_to_annotation_queue,
    sync_all_langsmith_assets,
    sync_langsmith_benchmark_dataset,
)


def test_get_langsmith_client_no_key(monkeypatch):
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    client = get_langsmith_client()
    assert client is None


def test_resolve_run_id_valid_uuid():
    mock_client = MagicMock()
    valid_uuid = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
    resolved = _resolve_run_id(mock_client, valid_uuid)
    assert resolved == valid_uuid


def test_resolve_run_id_from_project_runs():
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    mock_client.list_runs.return_value = [mock_run]

    resolved = _resolve_run_id(mock_client, "short-thread")
    assert resolved == "f47ac10b-58cc-4372-a567-0e02b2c3d479"


def test_log_critic_feedback():
    with patch(
        "langgraph_multi_agent_system.langsmith_utils.get_langsmith_client"
    ) as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client

        # Score out of 100 should normalize to 0.95
        success = log_critic_feedback("a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d", 95.0)
        assert success is True
        mock_client.create_feedback.assert_called_once()
        call_kwargs = mock_client.create_feedback.call_args[1]
        assert call_kwargs["score"] == 0.95


def test_get_or_create_annotation_queue():
    with patch(
        "langgraph_multi_agent_system.langsmith_utils.get_langsmith_client"
    ) as mock_get:
        mock_client = MagicMock()
        mock_q = MagicMock()
        mock_q.id = "queue-uuid-1234"
        mock_q.name = "test-queue"
        mock_client.list_annotation_queues.return_value = [mock_q]
        mock_get.return_value = mock_client

        qid = get_or_create_annotation_queue("test-queue")
        assert qid == "queue-uuid-1234"


def test_push_to_annotation_queue():
    with (
        patch(
            "langgraph_multi_agent_system.langsmith_utils.get_langsmith_client"
        ) as mock_get,
        patch(
            "langgraph_multi_agent_system.langsmith_utils.get_or_create_annotation_queue",
            return_value="queue-uuid",
        ),
    ):
        mock_client = MagicMock()
        mock_get.return_value = mock_client

        valid_uuid = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
        success = push_to_annotation_queue(valid_uuid, "nexus-human-review-queue")
        assert success is True
        mock_client.add_runs_to_annotation_queue.assert_called_once()


def test_sync_langsmith_benchmark_dataset():
    with patch(
        "langgraph_multi_agent_system.langsmith_utils.get_langsmith_client"
    ) as mock_get:
        mock_client = MagicMock()
        mock_ds = MagicMock()
        mock_ds.id = "dataset-uuid-999"
        mock_client.list_datasets.return_value = [mock_ds]
        mock_client.list_examples.return_value = ["example1"]
        mock_get.return_value = mock_client

        ds_id = sync_langsmith_benchmark_dataset("test-dataset")
        assert ds_id == "dataset-uuid-999"


def test_push_all_prompts_to_hub():
    with patch(
        "langgraph_multi_agent_system.langsmith_utils.get_langsmith_client"
    ) as mock_get:
        mock_client = MagicMock()
        mock_client.push_prompt.return_value = (
            "https://eu.smith.langchain.com/prompts/test"
        )
        mock_get.return_value = mock_client

        res = push_all_prompts_to_hub()
        assert len(res) == 5
        assert "nexus-supervisor-prompt" in res
        assert "nexus-writer-prompt" in res


def test_sync_all_langsmith_assets():
    with (
        patch(
            "langgraph_multi_agent_system.langsmith_utils.sync_langsmith_benchmark_dataset",
            return_value="ds-123",
        ),
        patch(
            "langgraph_multi_agent_system.langsmith_utils.get_or_create_annotation_queue",
            return_value="queue-123",
        ),
        patch(
            "langgraph_multi_agent_system.langsmith_utils.push_all_prompts_to_hub",
            return_value={"prompt1": "url1"},
        ),
        patch(
            "langgraph_multi_agent_system.langsmith_utils.run_langsmith_evaluation",
            return_value="exp-123",
        ),
    ):
        summary = sync_all_langsmith_assets()
        assert summary["dataset_id"] == "ds-123"
        assert summary["annotation_queue_id"] == "queue-123"
        assert summary["experiment_name"] == "exp-123"
        assert "prompt1" in summary["prompts_published"]
