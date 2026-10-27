"""Pytest configuration and test isolation fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def disable_tracing_for_tests():
    """Ensure automated tests run purely offline without attempting background network trace uploads."""
    old_tracing = os.environ.get("LANGCHAIN_TRACING_V2")
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    yield
    if old_tracing is not None:
        os.environ["LANGCHAIN_TRACING_V2"] = old_tracing
    else:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
