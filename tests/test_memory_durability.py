"""Tests for thread-safe, atomic PersistentDiskStore memory durability and tenant isolation."""

import concurrent.futures
import json
import os

from langgraph_multi_agent_system.memory_store import (
    PersistentDiskStore,
    get_tenant_namespace,
    recall_prior_knowledge,
)


def test_persistent_disk_store_durability_and_multi_namespace(tmp_path):
    """Verify that records across arbitrary namespaces persist across reloads."""
    mem_file = str(tmp_path / "test_memory.json")
    store = PersistentDiskStore(filepath=mem_file)

    # 1. Put in different namespaces
    store.put(("knowledge", "ai"), "paper1", {"title": "Graph Swarms", "score": 98})
    store.put(("tenants", "acme_corp", "preferences"), "tone", {"mode": "executive"})
    store.put(("users", "philippe"), "role", {"level": "principal"})

    assert os.path.exists(mem_file)

    # Inspect file contents format
    with open(mem_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == 1
    assert data["record_count"] >= 3

    # 2. Re-instantiate a fresh store from the same file (simulating restart)
    new_store = PersistentDiskStore(filepath=mem_file)
    res_knowledge = new_store.get(("knowledge", "ai"), "paper1")
    assert res_knowledge is not None
    assert res_knowledge.value["title"] == "Graph Swarms"

    res_tenant = new_store.get(("tenants", "acme_corp", "preferences"), "tone")
    assert res_tenant is not None
    assert res_tenant.value["mode"] == "executive"

    res_user = new_store.get(("users", "philippe"), "role")
    assert res_user is not None
    assert res_user.value["level"] == "principal"


def test_persistent_disk_store_concurrent_writes(tmp_path):
    """Verify that multiple concurrent threads can write without corrupting storage."""
    mem_file = str(tmp_path / "concurrent_memory.json")
    store = PersistentDiskStore(filepath=mem_file)

    def write_item(idx: int):
        ns = ("benchmarks", f"thread_{idx % 4}")
        store.put(ns, f"key_{idx}", {"idx": idx, "data": "concurrent_test"})
        return idx

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(write_item, i) for i in range(40)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 40

    # Ensure store can reload all 40 items without JSON corruption
    reloaded = PersistentDiskStore(filepath=mem_file)
    for i in range(40):
        ns = ("benchmarks", f"thread_{i % 4}")
        item = reloaded.get(ns, f"key_{i}")
        assert item is not None
        assert item.value["idx"] == i


def test_tenant_isolation_helpers(tmp_path):
    """Verify that tenant partitioning maintains isolated boundaries."""
    mem_file = str(tmp_path / "tenant_memory.json")
    store = PersistentDiskStore(filepath=mem_file)

    ns_tenant_a = get_tenant_namespace("tenant_A", category="finops")
    ns_tenant_b = get_tenant_namespace("tenant_B", category="finops")

    store.put(ns_tenant_a, "budget", {"max_tokens": 1000000})
    store.put(ns_tenant_b, "budget", {"max_tokens": 50000})

    item_a = store.get(ns_tenant_a, "budget")
    item_b = store.get(ns_tenant_b, "budget")

    assert item_a.value["max_tokens"] == 1000000
    assert item_b.value["max_tokens"] == 50000
    assert ns_tenant_a != ns_tenant_b


def test_recall_prior_knowledge_empty(tmp_path):
    """Verify safe fallback for empty knowledge store."""
    mem_file = str(tmp_path / "empty_memory.json")
    store = PersistentDiskStore(filepath=mem_file)
    results = recall_prior_knowledge(store, "non_existent_topic")
    assert isinstance(results, list)
    assert len(results) == 0
