"""Test configuration and fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def mock_api_credentials() -> tuple[int, str]:
    """Provide mock API credentials for testing.

    Returns:
        Tuple of (api_id, api_hash)

    """
    return (12345678, "abcdef1234567890abcdef1234567890")
