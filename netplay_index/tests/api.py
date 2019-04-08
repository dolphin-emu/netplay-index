"""Checks whether requests to / properly redirect to the Dolphin homepage"""

import json

from netplay_index.tests.base import NetPlayIndexTest
import tornado.util
from tornado.testing import gen_test

class ListTest(NetPlayIndexTest):
    @gen_test
    def runTest(self):
        response = yield self.http_client.fetch(self.get_url("/v0/list"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "OK")

class SessionAddTest(NetPlayIndexTest):

    @gen_test
    def bad_request(self):
        response = yield self.http_client.fetch(self.get_url("/v0/session/add"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "MISSING_PARAMETER")

    def runTest(self):
        self.bad_request()

class SessionActiveTest(NetPlayIndexTest):
    @gen_test
    def bad_request(self):
        response = yield self.http_client.fetch(self.get_url("/v0/session/active"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_SESSION")

    def runTest(self):
        self.bad_request()

class SessionRemoveTest(NetPlayIndexTest):

    @gen_test
    def bad_request(self):
        response = yield self.http_client.fetch(self.get_url("/v0/session/remove"))
        self.assertEqual(response.code, 200)

        body = json.loads(response.body)

        self.assertEqual(body["status"], "BAD_SESSION")

    def runTest(self):
        self.bad_request()
