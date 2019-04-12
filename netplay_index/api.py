"""Handle API requests"""

import re
import time

from tornado.web import RequestHandler

from netplay_index.util import check_origin, generate_secret, get_ip
import netplay_index
import netplay_index.database as database
import netplay_index.settings as settings
import netplay_index.sessions as sessions
import netplay_index.metrics as metrics

LAST_SESSION_CLEANUP = 0


def _cleanup_sessions():
    to_delete = []
    for key in sessions.get_all():
        if (
            time.time() - sessions.get_entry(key)["timestamp"]
            > settings.SESSION_TIMEOUT_SECONDS
        ):
            to_delete.append(key)

    for key in to_delete:
        sessions.remove_entry(key)


def _filter_string(sessions, key, value, match=False):
    filtered_sessions = []

    for session in sessions:
        if match:
            if re.search(re.escape(value), str(session[key]), re.IGNORECASE):
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

        if (
            sessions.get_host_session_count(get_ip(self))
            >= settings.MAXIMUM_SESSIONS_PER_HOST
        ):
            self.write({"status": "TOO_MANY_SESSIONS"})
            self.set_status(429)
            return

        new_session = {}
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
            new_session[key] = self.get_argument(key, default=None, strip=True)
            if new_session[key] is None:
                self.write({"status": "MISSING_PARAMETER", "parameter": key})
                self.set_status(400)
                return
            if not 0 < len(new_session[key]) < settings.SESSION_MAX_STRING_LENGTH:
                self.write({"status": "BAD_PARAMETER_LENGTH", "parameter": key})
                self.set_status(400)
                return
            if database.is_string_blacklisted(new_session[key]):
                self.write({"status": "BLACKLISTED_WORD", "parameter": key})
                self.set_status(400)
                return

        if new_session["region"] not in settings.VALID_REGIONS:
            self.write({"status": "BAD_REGION"})
            self.set_status(400)
            return

        if not 0 < int(new_session["port"]) <= 65535:
            self.write({"status": "BAD_PORT"})
            self.set_status(400)
            return

        if new_session["method"] not in ["direct", "traversal"]:
            self.write({"status": "BAD_METHOD"})
            self.set_status(400)
            return

        new_session["timestamp"] = time.time()

        try:
            new_session["in_game"] = bool(int(new_session["in_game"]))
            new_session["password"] = bool(int(new_session["password"]))

            new_session["port"] = int(new_session["port"])
            new_session["player_count"] = int(new_session["player_count"])
        except ValueError:
            self.write({"status": "PARSE_ERROR"})
            self.set_status(400)
            return

        ip = get_ip(self)
        secret = sessions.add_entry(new_session, ip)

        self.write({"status": "OK", "secret": secret})

    def session_active(self):
        """Keeps a session alive and updates some details"""
        secret = self.get_argument("secret", default=None, strip=True)
        game = self.get_argument("game", default=None, strip=True)
        in_game = self.get_argument("in_game", default=None, strip=True)
        player_count = self.get_argument("player_count", default=None, strip=True)

        if sessions.get_entry(secret) is None:
            self.write({"status": "BAD_SESSION"})
            self.set_status(400)
            return

        sessions.SESSIONS[secret]["timestamp"] = time.time()

        if game is not None:
            if database.is_string_blacklisted(game):
                self.write({"status": "BLACKLISTED_WORD", "parameter": "game"})
                self.set_status(400)
                return
            sessions.SESSIONS[secret]["game"] = game

        try:
            if in_game is not None:
                sessions.SESSIONS[secret]["in_game"] = bool(int(in_game))
            if player_count is not None:
                sessions.SESSIONS[secret]["player_count"] = int(player_count)
        except ValueError:
            self.write({"status": "PARSE_ERROR"})
            self.set_status(400)
            return

        self.write({"status": "OK"})

    def session_remove(self):
        """Removes a session"""
        secret = self.get_argument("secret", default=None, strip=True)

        if sessions.get_entry(secret) is None:
            self.write({"status": "BAD_SESSION"})
            self.set_status(400)
            return

        sessions.remove_entry(secret)

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

        filtered_sessions = list(sessions.get_all().values())

        if name is not None:
            filtered_sessions = _filter_string(filtered_sessions, "name", name, True)

        if game is not None:
            filtered_sessions = _filter_string(filtered_sessions, "game", game, True)

        if region is not None:
            filtered_sessions = _filter_string(filtered_sessions, "region", region)

        if version is not None:
            filtered_sessions = _filter_string(filtered_sessions, "version", version)

        try:
            if password is not None:
                filtered_sessions = _filter_string(
                    filtered_sessions, "password", bool(int(password))
                )

            if in_game is not None:
                filtered_sessions = _filter_string(
                    filtered_sessions, "in_game", bool(int(in_game))
                )
        except ValueError:
            self.write({"status": "PARSE_ERROR"})
            self.set_status(400)
            return

        self.write({"status": "OK", "sessions": filtered_sessions})

    def get(self, api_version, action):
        """Answer get requests"""
        api_version = int(api_version)
        metrics.API_REQUEST_COUNT.inc()
        if api_version != 0:
            self.write({"status": "BAD_VERSION"})
            self.set_status(400)
            return

        if not check_origin(self):
            self.write({"status": "BAD_ORIGIN"})
            self.set_status(403)
            return

        if database.is_host_banned(get_ip(self)):
            self.write({"status": "HOST_BANNED"})
            self.set_status(403)
            return

        actions = {
            "session/add": self.session_add,
            "session/remove": self.session_remove,
            "session/active": self.session_active,
            "list": self.list,
        }

        if action not in actions:
            self.write({"status": "BAD_ACTION"})
            self.set_status(404)
            return

        actions[action]()
