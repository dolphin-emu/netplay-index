"""Handle API requests"""

import re
import time

from tornado.web import RequestHandler

from netplay_index.util import check_origin, generate_secret, get_ip, get_ip_region
import netplay_index.database as database
import netplay_index.settings as settings

SESSIONS = {}
HOSTS = {}
REGIONS = {}

LAST_SESSION_CLEANUP = 0

def _cleanup_sessions():
    to_delete = []
    for key in SESSIONS:
        if time.time() - SESSIONS[key]["timestamp"] > settings.SESSION_TIMEOUT_SECONDS:
            to_delete.append(key)

    for key in to_delete:
        del SESSIONS[key]
        del HOSTS[key]
        del REGIONS[key]

def _filter_string(sessions, key, value, match=False):
    filtered_sessions = []

    for session in sessions:
        if match:
            if re.match(".*" + re.escape(value) + ".*", str(session[key]), re.IGNORECASE):
                filtered_sessions.append(session)
        else:
            if session[key] == value:
                filtered_sessions.append(session)

    return filtered_sessions


# pylint: disable=W0223
class Handler(RequestHandler):
    """Handler for all API requests"""

    def session_add(self):
        """Adds a new session"""

        if not check_origin(self):
            self.write({"status": "BAD_ORIGIN"})
            return

        if list(HOSTS.values()).count(get_ip(self)) > settings.MAXIMUM_SESSIONS_PER_HOST:
            self.write({"status": "TOO_MANY_SESSIONS"})
            return

        session = {}
        for key in [
            "name",
            "region",
            "game",
            "server_id",
            "port",
            "player_count",
            "in_game",
            "password",
            "version",
            "method",
        ]:
            session[key] = self.get_argument(key, default=None, strip=True)
            if session[key] is None:
                self.write({"status": "MISSING_PARAMETER", "parameter": key})
                return
            if database.is_string_blacklisted(session[key]):
                self.write({"status": "BLACKLISTED_WORD", "parameter": key})
                return

        if session["region"] not in settings.VALID_REGIONS:
            self.write({"status": "BAD_REGION"})
            return

        if not 0 < len(session["name"]) < settings.SESSION_MAX_STRING_LENGTH:
            self.write({"status": "BAD_NAME_LENGTH"})
            return

        if not 0 < len(session["game"]) < settings.SESSION_MAX_STRING_LENGTH:
            self.write({"status": "BAD_GAME_LENGTH"})
            return

        if not 0 < len(session["server_id"]) < settings.SESSION_MAX_STRING_LENGTH:
            self.write({"status": "BAD_SERVER_ID_LENGTH"})
            return

        if not 0 < int(session["port"]) <= 65535:
            self.write({"status": "BAD_PORT"})
            return

        if session["method"] not in ["direct", "traversal"]:
            self.write({"status": "BAD_METHOD"})
            return

        session["timestamp"] = time.time()

        try:
            session["in_game"] = bool(int(session["in_game"]))
            session["password"] = bool(int(session["password"]))

            session["port"] = int(session["port"])
            session["player_count"] = int(session["player_count"])
        except ValueError:
            self.write({"status": "PARSING_ERROR"})
            return

        secret = generate_secret()

        SESSIONS[secret] = session

        HOSTS[secret] = get_ip(self)

        REGIONS[secret] = get_ip_region(HOSTS[secret])

        self.write({"status": "OK", "secret": secret})

    def session_active(self):
        """Keeps a session alive and updates some details"""
        secret = self.get_argument("secret", default=None, strip=True)
        game = self.get_argument("game", default=None, strip=True)
        in_game = self.get_argument("in_game", default=None, strip=True)
        player_count = self.get_argument("player_count", default=None, strip=True)

        if secret not in SESSIONS:
            self.write({"status": "BAD_SESSION"})
            return

        SESSIONS[secret]["timestamp"] = time.time()

        if game is not None:
            if database.is_string_blacklisted(game):
                self.write({"status": "BLACKLISTED_WORD", "parameter": "game"})
                return
            SESSIONS[secret]["game"] = game

        if in_game is not None:
            try:
                SESSIONS[secret]["in_game"] = bool(int(in_game))
            except ValueError:
                self.write({"status": "PARSING_ERROR"})
                return

        if player_count is not None:
            try:
                SESSIONS[secret]["player_count"] = int(player_count)
            except ValueError:
                self.write({"status": "PARSING_ERROR"})
                return


        self.write({"status": "OK"})

    def session_remove(self):
        """Removes a session"""
        secret = self.get_argument("secret", default=None, strip=True)

        if secret not in SESSIONS:
            self.write({"status": "BAD_SESSION"})
            return

        del SESSIONS[secret]
        del HOSTS[secret]

        self.write({"status": "OK"})

    def list(self):
        """List all sessions matching filter"""
        # pylint: disable=W0603
        global LAST_SESSION_CLEANUP

        if time.time() - LAST_SESSION_CLEANUP > settings.SESSION_CLEANUP_DELAY:
            LAST_SESSION_CLEANUP = time.time()
            _cleanup_sessions()

        name = self.get_argument("name", default=None)
        game = self.get_argument("game", default=None)
        password = self.get_argument("password", default=None)
        region = self.get_argument("region", default=None)
        version = self.get_argument("version", default=None)
        in_game = self.get_argument("in_game", default=None)

        sessions = list(SESSIONS.values())

        if name is not None:
            sessions = _filter_string(sessions, "name", name, True)

        if game is not None:
            sessions = _filter_string(sessions, "game", game, True)

        if region is not None:
            sessions = _filter_string(sessions, "region", region)

        if version is not None:
            sessions = _filter_string(sessions, "version", version)

        try:
            if password is not None:
                sessions = _filter_string(sessions, "password", bool(int(password)))

            if in_game is not None:
                sessions = _filter_string(sessions, "in_game", bool(int(in_game)))
        except ValueError:
            self.write({"status": "PARSE_ERROR"})
            return

        self.write({"status": "OK", "sessions": sessions})

    def get(self, api_version, action):
        """Answer get requests"""
        api_version = int(api_version)
        if api_version != 0:
            self.write({"status": "BAD_VERSION"})
            return

        if not check_origin(self):
            self.write({"status": "BAD_ORIGIN"})
            return

        if database.is_host_banned(get_ip(self)):
            self.write({"status": "IP_BANNED"})
            return

        actions = {
            "session/add": self.session_add,
            "session/remove": self.session_remove,
            "session/active": self.session_active,
            "list": self.list,
        }

        if action not in actions:
            self.write({"status": "BAD_ACTION"})
            return

        actions[action]()
