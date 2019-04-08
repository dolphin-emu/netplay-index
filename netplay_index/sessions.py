"""Handle sessions"""

from netplay_index.util import generate_secret, get_ip_region

SESSIONS = {}
HOSTS = {}
REGIONS = {}


def get_all():
    return SESSIONS


def count():
    return len(SESSIONS)


def get_entry(secret):
    if secret not in SESSIONS:
        return None
    return SESSIONS[secret]


def add_entry(session, host):
    secret = generate_secret()
    SESSIONS[secret] = session
    HOSTS[secret] = host
    REGIONS[secret] = get_ip_region(host)
    return secret


def remove_entry(secret):
    del SESSIONS[secret]
    del HOSTS[secret]
    del REGIONS[secret]


def hosts():
    return HOSTS


def regions():
    return REGIONS


def get_host_session_count(ip):
    return list(HOSTS.values()).count(ip)
