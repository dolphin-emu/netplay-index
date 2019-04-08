"""Checks whether the API functions properly"""

import json

import tornado.util
from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest
import netplay_index.sessions as sessions
import netplay_index.database as database


class ListTest(NetPlayIndexTest):
    @gen_test
    def runTest(self):
        response = yield self.http_client.fetch(self.get_url("/v0/list"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "OK")


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

        # PARSING_ERROR
        response = yield self.http_client.fetch(self.build_url(in_game="yes"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "PARSING_ERROR")

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
    def test_valid_request(self):
        """Valid request with all required parameters"""
        response = yield self.http_client.fetch(self.build_url())
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "OK")


class SessionActiveTest(NetPlayIndexTest):
    """Tests for session/active"""

    @gen_test
    def test_bad_request(self):
        """Bad request with missing parameters"""
        response = yield self.http_client.fetch(self.get_url("/v0/session/active"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_SESSION")

    @gen_test
    def test_valid_request(self):
        """Valid request"""
        # Add faux session
        secret = sessions.add_entry({}, "127.0.0.1")

        response = yield self.http_client.fetch(
            self.get_url(
                "/v0/session/active?secret={}&player_count=10&in_game=1".format(secret)
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
