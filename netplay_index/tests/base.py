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

    async def login(self, bad_login=False, bad_pw=False):
        username = "test_user"
        password = "abc"

        if database.login_exists(username):
            database.delete_login(username)

        database.add_login(username, password, sysop=True)

        if bad_pw:
            password = "def"

        if bad_login:
            username = "test_user2"

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
                body="_xsrf={}&username={}&password={}".format(
                    xsrf, username, password
                ),
            )
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, 302)
            return e.response.headers["Set-Cookie"]

        if bad_pw or bad_login:
            self.assertEqual(response.code, 200)
        else:
            self.assertEqual(response, None)
