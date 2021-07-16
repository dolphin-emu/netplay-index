import json
import time

from bs4 import BeautifulSoup

import tornado.util
from tornado.testing import AsyncHTTPTestCase

import netplay_index.__main__ as netplay_index
import netplay_index.settings as settings
import netplay_index.sessions as sessions

import netplay_index.database as database


class NetPlayIndexTest(AsyncHTTPTestCase):
    """Base class for tests"""

    def get_app(self):
        # This greatly speeds up running tests
        settings.LOGIN_ATTEMPT_DELAY = 0
        app = netplay_index.make_app()

        # Many tests require a session to perform actions on
        session = {
            "name": "My Server",
            "region": "EU",
            "method": "direct",
            "password": False,
            "in_game": True,
            "port": 2626,
            "server_id": "test.id",
            "player_count": 2,
            "game": "Some Game",
            "version": "5.0-666",
            "revision": "58d0e223547dd111d3e8975ad6ff7f1988fbddfe",
        }

        # Pretend that we are from the future so the test definitely has enough time to pass
        sessions.add_entry(
            self.generate_session(timestamp=time.time() + 100), "8.8.8.8"
        )

        # Pretend this session is old so the clean-up process is triggered
        sessions.add_entry(
            self.generate_session(timestamp=time.time() - 100), "8.8.8.8"
        )

        return app

    def generate_session(self, timestamp=time.time()):
        return {
            "name": "My Server",
            "region": "EU",
            "method": "traversal",
            "password": False,
            "in_game": True,
            "port": 2626,
            "server_id": "test.id",
            "player_count": 2,
            "game": "Some Game",
            "version": "5.0-666",
            "revision": "58d0e223547dd111d3e8975ad6ff7f1988fbddfe",
            "timestamp": timestamp,
        }

    async def bad_request(self, expected_code, expected_status, http_args):
        response = None
        try:
            response = await self.http_client.fetch(**http_args)
        except tornado.httpclient.HTTPClientError as e:
            self.assertEqual(e.code, expected_code)
            body = json.loads(e.response.body)
            self.assertEqual(body["status"], expected_status)

        self.assertEqual(response, None)

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
            if bad_pw or bad_login:
                self.assertEqual(e.code, 403)
                return None
            else:
                self.assertEqual(e.code, 302)
                return e.response.headers["Set-Cookie"]

        self.assertEqual(response, None)
