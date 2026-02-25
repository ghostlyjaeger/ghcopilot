import copy

import pytest
from fastapi.testclient import TestClient

from src import app as application_module


# Snapshot the initial in-memory activities so tests can restore state
_SNAPSHOT = copy.deepcopy(application_module.activities)


@pytest.fixture
def client():
    """Provide a TestClient and restore `application_module.activities` before each test.

    This keeps tests isolated: each test starts from the same baseline data.
    """
    # Restore baseline state before each test
    application_module.activities = copy.deepcopy(_SNAPSHOT)

    with TestClient(application_module.app) as client:
        yield client
