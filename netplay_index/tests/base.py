import tornado.util
from tornado.testing import AsyncHTTPTestCase

import netplay_index.__main__ as netplay_index
import netplay_index.settings as settings


class NetPlayIndexTest(AsyncHTTPTestCase):
    def get_app(self):
        # This greatly speeds up running tests
        settings.LOGIN_ATTEMPT_DELAY = 0
        return netplay_index.make_app()
