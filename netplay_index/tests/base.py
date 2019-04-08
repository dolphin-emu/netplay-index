import tornado.util
from tornado.testing import AsyncHTTPTestCase

import netplay_index.__main__ as netplay_index

class NetPlayIndexTest(AsyncHTTPTestCase):
    def get_app(self):
        return netplay_index.make_app()
