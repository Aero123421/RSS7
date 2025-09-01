import pytest

from settings import load_settings


def test_missing_env(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("CLIENT_ID", raising=False)
    monkeypatch.delenv("GUILD_ID", raising=False)
    with pytest.raises(RuntimeError) as exc:
        load_settings()
    assert "DISCORD_TOKEN" in str(exc.value)
    assert "CLIENT_ID" in str(exc.value)
    assert "GUILD_ID" in str(exc.value)
