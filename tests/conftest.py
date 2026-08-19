"""Shared fixtures.

Deliberately thin: the full harness (temp-file DB per test, factories) lands with
the test-harness issue. What is here is what the skeleton's tests need.
"""

import os
from collections.abc import Iterator

# Set before app modules are imported: `app.main` builds the app at import time,
# and that read of Settings is the boot check under test elsewhere in this suite.
TEST_TOKEN = "test-token"
os.environ["PRENGINE_TOKEN"] = TEST_TOKEN

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    """Clear the cached Settings around every test so env edits don't leak."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    """Client with no credentials attached."""
    return TestClient(app)


@pytest.fixture
def auth_client() -> TestClient:
    """Client carrying a valid bearer token."""
    return TestClient(app, headers={"Authorization": f"Bearer {TEST_TOKEN}"})
