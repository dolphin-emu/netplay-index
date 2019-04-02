'''Handle login logic'''

from tornado.web import RequestHandler

import database

class Logout(RequestHandler):

    def post(self):
        '''Handle logouts'''
        self.clear_cookie('logged_in')

        self.render('views/logout.html')

# pylint: disable=W0223
class Login(RequestHandler):
    '''Handles login requests'''
    def get(self):
        '''Handle login page'''
        if self.get_secure_cookie('logged_in'):
            self.redirect('/admin')
            return

        self.render('views/login.html')

    def post(self):
        '''Handle login attempts'''

        username = self.get_argument('username', default=None, strip=True)
        password = self.get_argument('password', default=None, strip=True)

        if database.check_login(username, password):
            self.set_secure_cookie('logged_in', username)
            self.redirect('/admin')
            return

        self.render('views/login.html', error='Login failed.')
