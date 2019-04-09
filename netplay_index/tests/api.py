"""Checks whether the API functions properly"""

import json

import tornado.util
from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest
import netplay_index.sessions as sessions
import netplay_index.settings as settings
import netplay_index.database as database


class BadRequestTest(NetPlayIndexTest):
    @gen_test
    def test_bad_version(self):
        """Bad version"""
        response = yield self.http_client.fetch(self.get_url("/v666/list"))
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_VERSION")

    @gen_test
    def test_bad_action(self):
        """Bad action"""
        response = yield self.http_client.fetch(self.get_url("/v0/not_a_real_action"))
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_ACTION")

    @gen_test
    def test_banned(self):
        """Banned"""
        for entry in database.bans_get():
            if entry[0] == "3.3.3.3":
                database.ban_remove("3.3.3.3")
                break

        database.ban_add("3.3.3.3", "test_user", "test")
        response = yield self.http_client.fetch(
            self.get_url("/v0/list"), headers={"X-Real-IP": "3.3.3.3"}
        )
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)

        self.assertEqual(body["status"], "IP_BANNED")
        database.ban_remove("3.3.3.3")


class ListTest(NetPlayIndexTest):
    """Tests for /list"""

    @gen_test
    def test_valid_request(self):
        response = yield self.http_client.fetch(
            self.get_url(
                "/v0/list?name=server&region=EU&version=5.0-666&password=1&in_game=0&game=some"
            )
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "OK")

    @gen_test
    def test_bad_request(self):
        response = yield self.http_client.fetch(
            self.get_url(
                "/v0/list?name=foo&region=EU&version=5.0-666&password=bad&in_game=bad&game=foo"
            )
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "PARSE_ERROR")


class SessionAddTest(NetPlayIndexTest):
    """Tests for session/add"""

    def build_url(
        self,
        name="test",
        region="EU",
        game="None",
        in_game="1",
        password="1",
        player_count="10",
        server_id="1",
        method="direct",
        port="2626",
    ):
        """Return URL for testing purposes"""
        return self.get_url(
            "/v0/session/add?name={}&region={}&game={}&in_game={}&password={}&player_count={}&server_id={}&version=5.0-666&method={}&port={}".format(
                name,
                region,
                game,
                in_game,
                password,
                player_count,
                server_id,
                method,
                port,
            )
        )

    @gen_test
    def test_bad_requests(self):
        """Bad requests"""

        # MISSING_PARAMETER
        response = yield self.http_client.fetch(self.get_url("/v0/session/add"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "MISSING_PARAMETER")

        # BAD_REGEION
        response = yield self.http_client.fetch(self.build_url(region="??"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BAD_REGION")

        # PARSE_ERROR
        response = yield self.http_client.fetch(self.build_url(in_game="yes"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "PARSE_ERROR")

        # BAD_PORT
        response = yield self.http_client.fetch(self.build_url(port="123456"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BAD_PORT")

        # BAD_METHOD
        response = yield self.http_client.fetch(self.build_url(method="magic"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BAD_METHOD")

        # BAD_ORIGIN
        response = yield self.http_client.fetch(
            self.build_url(), headers={"Origin": "bad.origin"}
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BAD_ORIGIN")

        # BAD_PARAMETER_LENGTH
        response = yield self.http_client.fetch(
            self.build_url(name="A" * (settings.SESSION_MAX_STRING_LENGTH + 1))
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BAD_PARAMETER_LENGTH")

        # BLACKLISTED_WORD
        for entry in database.blacklist_get():
            if entry[0] == "nasty":
                database.blacklist_remove("nasty")
                break

        database.blacklist_add("nasty", "test_user", "it's a bad word")

        response = yield self.http_client.fetch(self.build_url(name="a+nasty+name"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BLACKLISTED_WORD")

        database.blacklist_remove("nasty")

    @gen_test
    def test_max_sessions(self):
        """Valid request with all required parameters"""

        for _ in range(0, settings.MAXIMUM_SESSIONS_PER_HOST):
            response = yield self.http_client.fetch(
                self.build_url(), headers={"X-Real-IP": "1.1.1.1"}
            )
            self.assertEqual(response.code, 200)

            body = json.loads(response.body)
            self.assertEqual(body["status"], "OK")

        response = yield self.http_client.fetch(
            self.build_url(), headers={"X-Real-IP": "1.1.1.1"}
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "TOO_MANY_SESSIONS")


class SessionActiveTest(NetPlayIndexTest):
    """Tests for session/active"""

    @gen_test
    def test_bad_requests(self):
        """Bad requests"""

        # BAD_SESSION
        response = yield self.http_client.fetch(self.get_url("/v0/session/active"))
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body["status"], "BAD_SESSION")

        # PARSE_ERROR
        secret = sessions.add_entry({}, "127.0.0.1")
        response = yield self.http_client.fetch(
            self.get_url("/v0/session/active?secret=" + secret + "&player_count=bad")
        )
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body["status"], "PARSE_ERROR")

        # BLACKLISTED_WORD
        for entry in database.blacklist_get():
            if entry[0] == "nasty":
                database.blacklist_remove("nasty")
                break

        database.blacklist_add("nasty", "test_user", "it's a bad word")

        response = yield self.http_client.fetch(
            self.get_url("/v0/session/active?secret=" + secret + "&game=a+nasty+name")
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "BLACKLISTED_WORD")

        database.blacklist_remove("nasty")

    @gen_test
    def test_valid_request(self):
        """Valid request"""
        # Add faux session
        secret = sessions.add_entry({}, "127.0.0.1")

        response = yield self.http_client.fetch(
            self.get_url(
                "/v0/session/active?secret={}&player_count=10&game=foo&in_game=1".format(
                    secret
                )
            )
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "OK")


class SessionRemoveTest(NetPlayIndexTest):
    """Tests for session/remove"""

    @gen_test
    def test_bad_request(self):
        """Bad request"""
        response = yield self.http_client.fetch(self.get_url("/v0/session/remove"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_SESSION")

    @gen_test
    def test_valid_request(self):
        """Valid request"""

        # Add faux session
        secret = sessions.add_entry({}, "127.0.0.1")

        response = yield self.http_client.fetch(
            self.get_url("/v0/session/remove?secret={}".format(secret))
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "OK")
