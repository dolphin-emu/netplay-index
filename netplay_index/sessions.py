"""Handle sessions"""

import time

from netplay_index.util import generate_secret, get_ip_region
import netplay_index.metrics as metrics

SESSIONS = {}
HOSTS = {}
REGIONS = {}


start_time = time.asctime(time.localtime())
total_session_count = 0


def get_all():
    return SESSIONS


def count():
    return len(SESSIONS)


def get_entry(secret):
    if secret not in SESSIONS:
        return None
    return SESSIONS[secret]


def add_entry(session, host):
    global total_session_count

    secret = generate_secret()
    SESSIONS[secret] = session
    HOSTS[secret] = host
    REGIONS[secret] = get_ip_region(host)
    total_session_count += 1

    metrics.API_SESSION_COUNT.inc()
    metrics.API_ACTIVE_SESSION_COUNT.inc()
    metrics.API_SESSION_DETAILS_COUNT.labels(
        game=session["game"],
        password=session["password"],
        method=session["method"],
        version=session["version"],
    ).inc()

    return secret


def remove_entry(secret):
    del SESSIONS[secret]
    del HOSTS[secret]
    del REGIONS[secret]

    metrics.API_ACTIVE_SESSION_COUNT.dec()


def hosts():
    return HOSTS


def regions():
    return REGIONS


def get_host_session_count(ip):
    return list(HOSTS.values()).count(ip)
