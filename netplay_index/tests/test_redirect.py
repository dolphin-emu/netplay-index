"""Checks whether requests to / properly redirect to the Dolphin homepage"""

from netplay_index.tests.base import NetPlayIndexTest
import tornado.util
from tornado.httpclient import HTTPClientError
from tornado.testing import gen_test


class RedirectTest(NetPlayIndexTest):
    @gen_test
    def runTest(self):
        with self.assertRaises(HTTPClientError) as cm:
            yield self.http_client.fetch(self.get_url("/"), follow_redirects=False)
        self.assertEqual(
            cm.exception.response.headers["Location"], "https://dolphin-emu.org"
        )
