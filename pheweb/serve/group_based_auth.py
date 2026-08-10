from ..conf_utils import conf
import logging
import sys
import threading
import time
from collections import defaultdict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# Google group membership rarely changes, but before_request() calls
# verify_membership() on every request, so cache results per-process for
# a while to avoid hitting the Admin SDK on every page load.
_MEMBERSHIP_CACHE_TTL_SECONDS = 300
_membership_cache = {}
_membership_cache_lock = threading.Lock()

if conf["authentication"]:
    group_names = conf.group_auth["GROUPS"]
    service_account_file = conf.group_auth["SERVICE_ACCOUNT_FILE"]
    delegated_account = conf.group_auth["DELEGATED_ACCOUNT"]

    service_account_scopes = [
        "https://www.googleapis.com/auth/admin.directory.group.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
        "https://www.googleapis.com/auth/admin.directory.group.member.readonly",
    ]

    # set credentials
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=service_account_scopes
    )
    delegated_creds = creds.with_subject(delegated_account)
    services = defaultdict(
        lambda: build("admin", "directory_v1", credentials=delegated_creds)
    )

    whitelist = conf.login["whitelist"] if "whitelist" in conf.login.keys() else []

else:
    group_names = []
    service_account_file = None
    delegated_account = None
    service_account_scopes = None
    creds = None
    delegated_creds = None
    services = None
    whitelist = None


def get_all_members(group_names):
    members = []
    for name in group_names:
        all = services[threading.get_ident()].members().list(groupKey=name).execute()
        members.extend(all["members"])
    return members


def verify_membership(username):

    if username in whitelist:
        return True
    # auth service .hasMember will only work for accounts of the domain
    elif not username.endswith("@finngen.fi"):
        return False

    now = time.monotonic()
    with _membership_cache_lock:
        cached = _membership_cache.get(username)
    if cached is not None and now - cached[0] < _MEMBERSHIP_CACHE_TTL_SECONDS:
        return cached[1]

    result, definitive = _check_group_membership(username)

    # Only cache a definitive answer. If some group check errored out and we
    # never found a match, we don't actually know the membership status, so
    # don't let a transient API failure get cached as "not a member".
    if definitive:
        with _membership_cache_lock:
            _membership_cache[username] = (now, result)
    return result


def _check_group_membership(username):
    """Returns (is_member, definitive). definitive is False if a group check
    errored out without us finding a match, meaning the result is not known
    for certain and should not be cached."""
    definitive = True
    for name in group_names:
        try:
            r = (
                services[threading.get_ident()]
                .members()
                .hasMember(groupKey=name, memberKey=username)
                .execute()
            )
        except HttpError:
            logging.exception("membership check failed for %r in group %r", username, name)
            definitive = False
            continue
        if r["isMember"] is True:
            return True, True
    # default to false
    return False, definitive
