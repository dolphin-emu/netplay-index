"""Checks whether the API functions properly"""

import json

import tornado.util
from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest
import netplay_index.sessions as sessions


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
    def bad_request(self):
        """Bad request with missing parameters"""
        response = yield self.http_client.fetch(self.get_url("/v0/session/add"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "MISSING_PARAMETER")

    @gen_test
    def valid_request(self):
        """Valid request with all required parameters"""
        response = yield self.http_client.fetch(self.build_url())
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)
        self.assertEqual(body["status"], "OK")

    def runTest(self):
        self.bad_request()
        self.valid_request()


class SessionActiveTest(NetPlayIndexTest):
    """Tests for session/active"""

    @gen_test
    def bad_request(self):
        """Bad request with missing parameters"""
        response = yield self.http_client.fetch(self.get_url("/v0/session/active"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_SESSION")

    @gen_test
    def valid_request(self):
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

    def runTest(self):
        self.bad_request()
        self.valid_request()


class SessionRemoveTest(NetPlayIndexTest):
    """Tests for session/remove"""

    @gen_test
    def bad_request(self):
        """Bad request"""
        response = yield self.http_client.fetch(self.get_url("/v0/session/remove"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_SESSION")

    @gen_test
    def valid_request(self):
        """Valid request"""

        # Add faux session
        secret = sessions.add_entry({}, "127.0.0.1")

        response = yield self.http_client.fetch(
            self.get_url("/v0/session/remove?secret={}".format(secret))
        )
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "OK")

    def runTest(self):
        self.bad_request()
        self.valid_request()
