# -*- coding: utf-8 -*-

"""
Unit tests for group_based_auth module.

See: pheweb/serve/group_based_auth.py
"""
from collections import defaultdict
from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from pheweb.serve import group_based_auth
from pheweb.serve.group_based_auth import (
    verify_membership,
    get_all_members,
    _check_group_membership,
)


def _http_error():
    """Build a minimal HttpError, as raised by the Google API client."""
    return HttpError(MagicMock(status=500, reason="boom"), b"{}")


def _fake_services(group_outcomes):
    """
    Build a fake `services` defaultdict (as used by group_based_auth,
    keyed by thread id) whose `.members().hasMember(groupKey=...)` calls
    are driven by `group_outcomes`: a dict mapping group name to either
    a bool (the `isMember` result) or an Exception instance to raise.

    @param group_outcomes: dict of group name -> bool or Exception
    @return: (fake services defaultdict, list recording each group name queried)
    """
    calls = []

    def has_member(groupKey, memberKey):
        calls.append(groupKey)
        outcome = group_outcomes[groupKey]
        request = MagicMock()
        if isinstance(outcome, Exception):
            request.execute.side_effect = outcome
        else:
            request.execute.return_value = {"isMember": outcome}
        return request

    members = MagicMock()
    members.hasMember.side_effect = has_member
    service = MagicMock()
    service.members.return_value = members
    return defaultdict(lambda: service), calls


@pytest.fixture(autouse=True)
def _clear_membership_cache(monkeypatch):
    """Every test starts with an empty, isolated membership cache."""
    monkeypatch.setattr(group_based_auth, "_membership_cache", {})


def test_verify_membership_whitelisted(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", ["alice@example.com"])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    # services is left as None: touching it would error, proving no API call was made.
    monkeypatch.setattr(group_based_auth, "services", None)
    assert verify_membership("alice@example.com") is True


def test_verify_membership_non_domain_user_rejected(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    monkeypatch.setattr(group_based_auth, "services", None)
    assert verify_membership("bob@example.com") is False


def test_verify_membership_member_of_second_group(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1", "g2"])
    services, calls = _fake_services({"g1": False, "g2": True})
    monkeypatch.setattr(group_based_auth, "services", services)

    assert verify_membership("carol@finngen.fi") is True
    assert calls == ["g1", "g2"]


def test_verify_membership_not_a_member_of_any_group(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1", "g2"])
    services, calls = _fake_services({"g1": False, "g2": False})
    monkeypatch.setattr(group_based_auth, "services", services)

    assert verify_membership("dave@finngen.fi") is False
    assert calls == ["g1", "g2"]


def test_verify_membership_api_error_fails_closed_but_checks_other_groups(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1", "g2"])
    services, calls = _fake_services({"g1": _http_error(), "g2": False})
    monkeypatch.setattr(group_based_auth, "services", services)

    # A failed check on g1 must not raise, and must not prevent g2 from being checked.
    assert verify_membership("frank@finngen.fi") is False
    assert calls == ["g1", "g2"]


def test_verify_membership_caches_definitive_result(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    services, calls = _fake_services({"g1": True})
    monkeypatch.setattr(group_based_auth, "services", services)

    assert verify_membership("grace@finngen.fi") is True
    assert verify_membership("grace@finngen.fi") is True
    assert calls == ["g1"]  # second call served from cache, no new API call


def test_verify_membership_does_not_cache_inconclusive_result(monkeypatch):
    """
    Regression test: if every group check errors out, the result must not be
    cached, since a transient API failure isn't a real "not a member" answer.
    Otherwise a brief outage would deny a real member for the whole TTL.
    """
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    services, calls = _fake_services({"g1": _http_error()})
    monkeypatch.setattr(group_based_auth, "services", services)

    assert verify_membership("hank@finngen.fi") is False
    assert verify_membership("hank@finngen.fi") is False
    assert calls == ["g1", "g1"]  # not cached: API hit again on the second call


def test_verify_membership_cache_expires_after_ttl(monkeypatch):
    monkeypatch.setattr(group_based_auth, "whitelist", [])
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    services, calls = _fake_services({"g1": True})
    monkeypatch.setattr(group_based_auth, "services", services)

    clock = iter([0, group_based_auth._MEMBERSHIP_CACHE_TTL_SECONDS + 1])
    monkeypatch.setattr(group_based_auth.time, "monotonic", lambda: next(clock))

    assert verify_membership("iris@finngen.fi") is True
    assert verify_membership("iris@finngen.fi") is True
    assert calls == ["g1", "g1"]  # cache had expired, so it re-checked


def test_check_group_membership_definitive_when_found(monkeypatch):
    monkeypatch.setattr(group_based_auth, "group_names", ["g1", "g2"])
    services, _ = _fake_services({"g1": False, "g2": True})
    monkeypatch.setattr(group_based_auth, "services", services)
    assert _check_group_membership("x@finngen.fi") == (True, True)


def test_check_group_membership_definitive_when_no_match(monkeypatch):
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    services, _ = _fake_services({"g1": False})
    monkeypatch.setattr(group_based_auth, "services", services)
    assert _check_group_membership("x@finngen.fi") == (False, True)


def test_check_group_membership_inconclusive_on_error(monkeypatch):
    monkeypatch.setattr(group_based_auth, "group_names", ["g1"])
    services, _ = _fake_services({"g1": _http_error()})
    monkeypatch.setattr(group_based_auth, "services", services)
    assert _check_group_membership("x@finngen.fi") == (False, False)


def test_get_all_members(monkeypatch):
    monkeypatch.setattr(group_based_auth, "group_names", ["g1", "g2"])

    def fake_list(groupKey):
        request = MagicMock()
        members_by_group = {
            "g1": [{"email": "a@finngen.fi"}],
            "g2": [{"email": "b@finngen.fi"}],
        }
        request.execute.return_value = {"members": members_by_group[groupKey]}
        return request

    members = MagicMock()
    members.list.side_effect = fake_list
    service = MagicMock()
    service.members.return_value = members
    monkeypatch.setattr(group_based_auth, "services", defaultdict(lambda: service))

    result = get_all_members(["g1", "g2"])
    assert result == [{"email": "a@finngen.fi"}, {"email": "b@finngen.fi"}]
