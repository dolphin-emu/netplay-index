"""Tests for the admin interface"""

import tornado.util
from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest


class LoginTest(NetPlayIndexTest):
    """Test for the login page"""

    @gen_test
    def runTest(self):
        response = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(response.code, 200)


# TODO: Test for /logout
# TODO: Test for /admin/overview
# TODO: Test for /admin/server_list
# TODO: Test for /admin/bans
# TODO: Test for /admin/blacklist
# TODO: Test for /admin/user_management
