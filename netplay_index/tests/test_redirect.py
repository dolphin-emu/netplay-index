"""Checks whether requests to / properly redirect to the Dolphin homepage"""

from netplay_index.tests.base import NetPlayIndexTest
import tornado.util
from tornado.testing import gen_test


class RedirectTest(NetPlayIndexTest):
    @gen_test
    def runTest(self):
        response = yield self.http_client.fetch(self.get_url("/"))
        self.assertEqual(response.effective_url, "https://dolphin-emu.org")
