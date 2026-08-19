"""Tests for app/config.py."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.main import create_app


def test_boot_fails_when_token_unset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An unset PRENGINE_TOKEN crashes at startup, never authenticates everyone."""
    monkeypatch.delenv("PRENGINE_TOKEN", raising=False)
    # Run from an empty directory so a developer's .env can't supply the token.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        create_app()
