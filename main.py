#!/usr/bin/env python3
'''Main module'''

import os

import tornado.ioloop
from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler

import admin
import api
import login
import database
import util

define('port', default=8000, help='Port to listen on', type=int)
define('add_sysop', default=None, help='Add a new sysop via the command line')
define('reset_pw', default=None, help='Reset the password of a given user')

# pylint: disable=W0223
class MainHandler(RequestHandler):
    '''Handler for root requests'''
    def get(self):
        '''Just sends away unwanted visitors'''
        self.redirect('https://dolphin-emu.org')

def make_app():
    '''Return new app'''
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/v(?P<api_version>\d+)/(?P<action>[\w/]+)', api.Handler),
        (r'/login', login.Handler),
        (r'/admin', admin.Handler),
    ], cookie_secret=os.urandom(32), xsrf_cookies=True,
                                   static_path=os.path.join(os.path.dirname(__file__), "static"))

if __name__ == '__main__':
    parse_command_line()
    if not database.initialize():
        exit(1)

    if options.add_sysop is not None:
        RANDOM_PW = util.generate_secret()
        database.add_login(options.add_sysop, RANDOM_PW, True)
        print('Password for {}: {}'.format(options.add_sysop, RANDOM_PW))
        exit(0)

    if options.reset_pw is not None:
        RANDOM_PW = util.generate_secret()
        database.update_login(options.reset_pw, RANDOM_PW)
        print('New password for {}: {}'.format(options.reset_pw, RANDOM_PW))
        exit(0)

    APP = make_app()
    APP.listen(options.port)
    print('Listening on port {}...'.format(options.port))
    tornado.ioloop.IOLoop.current().start()
