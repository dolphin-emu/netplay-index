"""Tests for /metrics"""

from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest


class MetricsTest(NetPlayIndexTest):
    @gen_test
    def test_get(self):
        response = yield self.http_client.fetch(self.get_url("/metrics"))
        self.assertEqual(response.code, 200)
