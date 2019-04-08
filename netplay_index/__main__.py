#!/usr/bin/env python3
"""Main module"""

import os

import tornado.ioloop
from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler

import netplay_index.api as api
import netplay_index.login as login
import netplay_index.database as database
import netplay_index.util as util
import netplay_index.admin as admin

define("port", default=8000, help="Port to listen on", type=int)
define("add_sysop", default=None, help="Add a new sysop via the command line")
define("reset_pw", default=None, help="Reset the password of a given user")

# pylint: disable=W0223
class MainHandler(RequestHandler):
    """Handler for root requests"""

    def get(self):
        """Just sends away unwanted visitors"""
        self.redirect("https://dolphin-emu.org")


def make_app():
    """Return new app"""

    if not database.initialize():
        return None

    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/v(?P<api_version>\d+)/(?P<action>[\w/]+)", api.Handler),
            (r"/login", login.login.Login),
            (r"/logout", login.login.Logout),
            (r"/admin/overview", admin.overview.Handler),
            (r"/admin/blacklist", admin.blacklist.Handler),
            (r"/admin/bans", admin.bans.Handler),
            (r"/admin/user_management", admin.user_management.Handler),
            (r"/admin/server_list", admin.server_list.Handler),
        ],
        cookie_secret=os.urandom(32),
        xsrf_cookies=True,
        static_path=os.path.join(os.path.dirname(__file__), "static"),
    )


if __name__ == "__main__":
    parse_command_line()

    APP = make_app()

    if APP is None:
        exit(1)

    if options.add_sysop is not None:
        RANDOM_PW = util.generate_secret()
        database.add_login(options.add_sysop, RANDOM_PW, True)
        print("Password for {}: {}".format(options.add_sysop, RANDOM_PW))
        exit(0)

    if options.reset_pw is not None:
        RANDOM_PW = util.generate_secret()
        database.update_login(options.reset_pw, RANDOM_PW)
        print("New password for {}: {}".format(options.reset_pw, RANDOM_PW))
        exit(0)

    APP.listen(options.port)
    print("Listening on port {}...".format(options.port))
    tornado.ioloop.IOLoop.current().start()
