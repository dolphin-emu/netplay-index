"""Utility class"""

import geoip2.database
import random

import netplay_index.settings as settings

SECRET_KEY_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
SECRET_KEY_LENGTH = 10

def get_ip_region(ip):
    reader = geoip2.database.Reader(settings.GEOIP_DATABASE_PATH)
    try:
        return reader.country(ip).country.iso_code.lower()
    except geoip2.errors.AddressNotFoundError:
        return None

def generate_secret():
    """Generate secret string from a pool of characters"""
    secret = ""

    for _ in range(0, SECRET_KEY_LENGTH):
        secret += random.choice(SECRET_KEY_CHARACTERS)

    return secret


def check_origin(handler):
    """Check whether we got a cross-origin request"""
    origin = handler.request.headers.get("Origin")

    if origin is None:
        return True

    return origin == handler.request.headers.get("Host")


def get_ip(handler):
    """Get IP properly, even when behind a proxy"""
    if handler.request.remote_ip in ["127.0.0.1", "::1", "localhost"]:
        real_ip = handler.request.headers.get("X-Real-IP")
        if real_ip is not None:
            return real_ip

    return handler.request.remote_ip
