"""Tests for the admin interface"""

import tornado.util
from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest

import netplay_index.database as database


class LoginTest(NetPlayIndexTest):
    """Test for the login page"""

    @gen_test
    def test_get(self):
        response = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(response.code, 200)

    @gen_test
    def test_post(self):
        yield self.login()
        database.delete_login("test_user")


class AdminOverviewTest(NetPlayIndexTest):
    """Test for /admin/overview"""

    @gen_test
    def test_get(self):
        cookie = yield self.login()

        response = yield self.http_client.fetch(
            self.get_url("/admin/overview"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")


class AdminServerListTest(NetPlayIndexTest):
    """Test for /admin/server_list"""

    @gen_test
    def test_get(self):

        cookie = yield self.login()

        response = yield self.http_client.fetch(
            self.get_url("/admin/server_list"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")


class AdminUserManagementTest(NetPlayIndexTest):
    """Test for /admin/user_management"""

    @gen_test
    def test_get(self):
        cookie = yield self.login()

        response = yield self.http_client.fetch(
            self.get_url("/admin/blacklist"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")


class AdminBansTest(NetPlayIndexTest):
    """Test for /admin/bans"""

    @gen_test
    def test_get(self):
        cookie = yield self.login()

        response = yield self.http_client.fetch(
            self.get_url("/admin/bans"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")


# TODO: Test for /logout
# TODO: Test for /admin/server_list
