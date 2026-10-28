"""Tests for thread-safe, multi-process ACID SqliteMemoryStore and PersistentDiskStore."""

import concurrent.futures
import json
import os

from langgraph_multi_agent_system.memory_store import (
    PersistentDiskStore,
    SqliteMemoryStore,
    get_tenant_namespace,
    recall_prior_knowledge,
)


def test_sqlite_memory_store_durability_and_reload(tmp_path):
    """Verify that SqliteMemoryStore commits to SQLite and survives process restart."""
    db_file = str(tmp_path / "test_memory.db")
    store = SqliteMemoryStore(db_path=db_file)

    store.put(
        ("knowledge", "logistics"), "bol_tariff", {"tariff": 250, "unit": "USD/day"}
    )
    store.put(
        ("tenants", "maersk_line", "finops"),
        "budget",
        {"monthly_limit": 50000},
    )

    assert os.path.exists(db_file)

    # Simulate fresh process opening the same SQLite DB
    new_process_store = SqliteMemoryStore(db_path=db_file)
    item = new_process_store.get(("knowledge", "logistics"), "bol_tariff")
    assert item is not None
    assert item.value["tariff"] == 250

    tenant_item = new_process_store.get(("tenants", "maersk_line", "finops"), "budget")
    assert tenant_item is not None
    assert tenant_item.value["monthly_limit"] == 50000


def test_sqlite_memory_store_concurrent_writes(tmp_path):
    """Verify that multiple concurrent threads can write to SQLite without locks failing."""
    db_file = str(tmp_path / "concurrent_sqlite.db")
    store = SqliteMemoryStore(db_path=db_file)

    def write_task(idx: int):
        ns = ("benchmarks", f"worker_{idx % 4}")
        store.put(ns, f"task_{idx}", {"idx": idx, "status": "completed"})
        return idx

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(write_task, i) for i in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 50

    reloaded = SqliteMemoryStore(db_path=db_file)
    for i in range(50):
        ns = ("benchmarks", f"worker_{i % 4}")
        item = reloaded.get(ns, f"task_{i}")
        assert item is not None
        assert item.value["idx"] == i


def test_persistent_disk_store_durability_and_multi_namespace(tmp_path):
    """Verify that records across arbitrary namespaces persist across reloads in JSON store."""
    mem_file = str(tmp_path / "test_memory.json")
    store = PersistentDiskStore(filepath=mem_file)

    store.put(("knowledge", "ai"), "paper1", {"title": "Graph Swarms", "score": 98})
    store.put(("tenants", "acme_corp", "preferences"), "tone", {"mode": "executive"})
    store.put(("users", "philippe"), "role", {"level": "principal"})

    assert os.path.exists(mem_file)

    with open(mem_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == 1
    assert data["record_count"] >= 3

    new_store = PersistentDiskStore(filepath=mem_file)
    res_knowledge = new_store.get(("knowledge", "ai"), "paper1")
    assert res_knowledge is not None
    assert res_knowledge.value["title"] == "Graph Swarms"

    res_tenant = new_store.get(("tenants", "acme_corp", "preferences"), "tone")
    assert res_tenant is not None
    assert res_tenant.value["mode"] == "executive"


def test_tenant_isolation_helpers(tmp_path):
    """Verify that tenant partitioning maintains isolated boundaries."""
    db_file = str(tmp_path / "tenant_memory.db")
    store = SqliteMemoryStore(db_path=db_file)

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
    db_file = str(tmp_path / "empty_memory.db")
    store = SqliteMemoryStore(db_path=db_file)
    results = recall_prior_knowledge(store, "non_existent_topic")
    assert isinstance(results, list)
    assert len(results) == 0
