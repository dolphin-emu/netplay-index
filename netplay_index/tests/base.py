from bs4 import BeautifulSoup

import tornado.util
from tornado.testing import AsyncHTTPTestCase

import netplay_index.__main__ as netplay_index
import netplay_index.settings as settings

import netplay_index.database as database


class NetPlayIndexTest(AsyncHTTPTestCase):
    """Base class for tests"""

    def get_app(self):
        # This greatly speeds up running tests
        settings.LOGIN_ATTEMPT_DELAY = 0
        return netplay_index.make_app()

    async def login(self):
        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc")

        get = await self.http_client.fetch(self.get_url("/login"))
        self.assertEqual(get.code, 200)

        soup = BeautifulSoup(get.body, "html.parser")
        xsrf = soup.find(attrs={"name": "_xsrf"})["value"]

        response = None
        try:
            response = await self.http_client.fetch(
                self.get_url("/login"),
                method="POST",
                follow_redirects=False,
                headers={"Cookie": "_xsrf={}".format(xsrf)},
                body="_xsrf={}&username=test_user&password=abc".format(xsrf),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            return e.response.headers["Set-Cookie"]
