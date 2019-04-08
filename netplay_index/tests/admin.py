"""Tests for the admin interface"""

import tornado.util
from tornado.testing import gen_test
from bs4 import BeautifulSoup

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
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        try:
            response = yield self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)

        database.delete_login("test_user")

        # If there was no redirect, the login attempt has failed
        self.assertEqual(response, None)


# The following tests are aboslute messes
# TODO: Separate them into individual files
# TODO: Deduplicate the login code
# TODO: Deduplicate the database handling


class AdminOverviewTest(NetPlayIndexTest):
    """Test for /admin/overview"""

    @gen_test
    def test_get(self):

        ### This block is copied and pasted from LoginTest as there are some issues with wrapping it into a function
        ### BEGIN LoginTest
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        cookie = None
        try:
            response = yield self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            cookie = e.response.headers["Set-Cookie"]

        # If there was no redirect, the login attempt has failed
        self.assertEqual(response, None)
        ### END LoginTest

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

        ### This block is copied and pasted from LoginTest as there are some issues with wrapping it into a function
        ### BEGIN LoginTest
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        cookie = None
        try:
            response = yield self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            cookie = e.response.headers["Set-Cookie"]

        # If there was no redirect, the login attempt has failed
        self.assertEqual(response, None)
        ### END LoginTest

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

        ### This block is copied and pasted from LoginTest as there are some issues with wrapping it into a function
        ### BEGIN LoginTest
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        cookie = None
        try:
            response = yield self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            cookie = e.response.headers["Set-Cookie"]

        # If there was no redirect, the login attempt has failed
        self.assertEqual(response, None)
        ### END LoginTest

        response = yield self.http_client.fetch(
            self.get_url("/admin/user_management"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")


class AdminBlacklistTest(NetPlayIndexTest):
    """Test for /admin/blacklist"""

    @gen_test
    def test_get(self):

        ### This block is copied and pasted from LoginTest as there are some issues with wrapping it into a function
        ### BEGIN LoginTest
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        cookie = None
        try:
            response = yield self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            cookie = e.response.headers["Set-Cookie"]

        # If there was no redirect, the login attempt has failed
        self.assertEqual(response, None)
        ### END LoginTest

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

        ### This block is copied and pasted from LoginTest as there are some issues with wrapping it into a function
        ### BEGIN LoginTest
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = yield self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        cookie = None
        try:
            response = yield self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            cookie = e.response.headers["Set-Cookie"]

        # If there was no redirect, the login attempt has failed
        self.assertEqual(response, None)
        ### END LoginTest

        response = yield self.http_client.fetch(
            self.get_url("/admin/bans"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")


# TODO: Test for /logout
# TODO: Test for /admin/server_list
