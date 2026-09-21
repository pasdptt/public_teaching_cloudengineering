"""Configuration errors must be actionable.

With one instructor and no teaching assistant, an unhelpful start-up error is a support
request. Each of these tests asserts that the message contains the thing the student needs
to know — the variable name, the allowed range, or an example.
"""

from __future__ import annotations

import pytest

from docapp.config import Config, ConfigError


def test_defaults_are_usable_with_an_empty_environment(monkeypatch):
    for var in ("DOCAPP_HOST", "PORT", "DOCAPP_STORAGE", "DOCAPP_JOBSTORE",
                "DOCAPP_QUEUE", "DOCAPP_DATA_DIR", "DOCAPP_LOG_LEVEL",
                "DOCAPP_MAX_DOCUMENT_BYTES", "DOCAPP_PROCESSING_DELAY_MS",
                "DOCAPP_INSTANCE_ID"):
        monkeypatch.delenv(var, raising=False)
    config = Config.from_env()
    assert config.port == 8080
    assert config.host == "127.0.0.1"       # not reachable from the network by default
    assert config.jobstore_backend == "memory"


def test_port_env_var_is_honoured(monkeypatch):
    """Managed execution platforms set $PORT. Honouring it is why Lab 4 needs no code change."""
    monkeypatch.setenv("PORT", "9999")
    assert Config.from_env().port == 9999


def test_non_numeric_port_names_the_variable_and_gives_an_example(monkeypatch):
    monkeypatch.setenv("PORT", "eighty-eighty")
    with pytest.raises(ConfigError) as exc:
        Config.from_env()
    message = str(exc.value)
    assert "PORT" in message and "whole number" in message and "Example" in message


def test_out_of_range_delay_explains_why_the_bound_exists(monkeypatch):
    monkeypatch.setenv("DOCAPP_PROCESSING_DELAY_MS", "600000")
    with pytest.raises(ConfigError) as exc:
        Config.from_env()
    assert "between 0 and 5000" in str(exc.value)


def test_unknown_backend_lists_the_valid_choices(monkeypatch):
    monkeypatch.setenv("DOCAPP_JOBSTORE", "postgres")
    with pytest.raises(ConfigError) as exc:
        Config.from_env()
    assert "memory" in str(exc.value) and "file" in str(exc.value)


def test_describe_contains_no_secret_shaped_keys(monkeypatch):
    """The resolved config is logged at start-up, so it must never carry a credential.

    Today there are no secrets in Config. This test exists so that the day someone adds
    one, the test fails and they have to think about it.
    """
    described = Config.from_env().describe()
    forbidden = ("key", "secret", "token", "password", "credential")
    assert not [k for k in described if any(f in k.lower() for f in forbidden)]
