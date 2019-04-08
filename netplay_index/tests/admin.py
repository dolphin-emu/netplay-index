"""Tests for the admin interface"""

from bs4 import BeautifulSoup

import tornado.util
from tornado.testing import gen_test

from netplay_index.tests.base import NetPlayIndexTest

import netplay_index.database as database


def _get_xsrf(body, action):
    soup = BeautifulSoup(body, "html.parser")

    return (
        soup.find(name="input", attrs={"name": "action", "value": action})
        .find_parent("form")
        .find(attrs={"name": "_xsrf"})["value"]
    )


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


class LogoutTest(NetPlayIndexTest):
    """Test for the logout page"""

    @gen_test
    def test_post(self):
        cookie = yield self.login()

        xsrf_response = yield self.http_client.fetch(
            self.get_url("/admin/overview"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )

        soup = BeautifulSoup(xsrf_response.body, "html.parser")
        xsrf = soup.find(name="form", attrs={"action": "/logout"}).find(
            attrs={"name": "_xsrf"}
        )["value"]

        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        cookie = xsrf_response.headers["Set-Cookie"]

        response = yield self.http_client.fetch(
            self.get_url("/logout"),
            method="POST",
            headers={"Cookie": cookie},
            body="_xsrf={}".format(xsrf),
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")

    @gen_test
    def test_post_bad(self):
        yield self.login(bad_pw=True)
        yield self.login(bad_login=True)


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


class AdminBlacklistTest(NetPlayIndexTest):
    """Test for /admin/blacklist"""

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

    @gen_test
    def test_post(self):
        login_cookie = yield self.login()

        get = yield self.http_client.fetch(
            self.get_url("/admin/blacklist"),
            headers={"Cookie": login_cookie},
            follow_redirects=False,
        )
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = (
            soup.find(name="input", attrs={"name": "action", "value": "blacklist_add"})
            .find_parent("form")
            .find(attrs={"name": "_xsrf"})["value"]
        )

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/blacklist"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=blacklist_add&word=test&reason=test".format(xsrf),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

        soup = BeautifulSoup(post.body, "html.parser")
        xsrf = (
            soup.find(
                name="input", attrs={"name": "action", "value": "blacklist_remove"}
            )
            .find_parent("form")
            .find(attrs={"name": "_xsrf"})["value"]
        )

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/blacklist"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=blacklist_remove&word=test".format(xsrf),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

        database.delete_login("test_user")


class AdminUserManagementTest(NetPlayIndexTest):
    """Test for /admin/user_management"""

    @gen_test
    def test_get(self):
        cookie = yield self.login()

        response = yield self.http_client.fetch(
            self.get_url("/admin/user_management"),
            headers={"Cookie": cookie},
            follow_redirects=False,
        )
        self.assertEqual(response.code, 200)

        database.delete_login("test_user")

    @gen_test
    def test_post(self):
        login_cookie = yield self.login()

        get = yield self.http_client.fetch(
            self.get_url("/admin/user_management"),
            headers={"Cookie": login_cookie},
            follow_redirects=False,
        )
        self.assertEqual(get.code, 200)

        xsrf = _get_xsrf(get.body, "create_user")

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/user_management"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=create_user&username=test-user2&password=b&sysop=1".format(
                xsrf
            ),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

        xsrf = _get_xsrf(post.body, "change_password")

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/user_management"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=change_password&username=test-user2&password=test".format(
                xsrf
            ),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

        xsrf = _get_xsrf(post.body, "delete_user")

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/user_management"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=delete_user&username=test-user2".format(xsrf),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

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

    @gen_test
    def test_post(self):
        login_cookie = yield self.login()

        get = yield self.http_client.fetch(
            self.get_url("/admin/bans"),
            headers={"Cookie": login_cookie},
            follow_redirects=False,
        )
        self.assertEqual(get.code, 200)

        xsrf = _get_xsrf(get.body, "ban_add")

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/bans"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=ban_add&host=test&reason=test".format(xsrf),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

        xsrf = _get_xsrf(post.body, "ban_remove")

        cookie = login_cookie + ";" + get.headers["Set-Cookie"]

        post = yield self.http_client.fetch(
            self.get_url("/admin/bans"),
            headers={"Cookie": cookie},
            method="POST",
            body="_xsrf={}&action=ban_remove&host=test".format(xsrf),
            follow_redirects=False,
        )
        self.assertEqual(post.code, 200)

        database.delete_login("test_user")
