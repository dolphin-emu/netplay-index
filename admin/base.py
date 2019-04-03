'''Base handler that all other admin views are based on'''

from tornado.web import RequestHandler

import api
import database

# pylint: disable=W0223
class AdminHandler(RequestHandler):
    '''Base handler'''
    def set_view(self, view):
        '''Set view to render'''
        self.view = view

    def set_error(self, error):
        '''Set error'''
        self.error = error

    def get_username(self):
        '''Get current username or None'''
        username = self.get_secure_cookie('logged_in')

        if username is None:
            return None

        return username.decode('UTF-8')

    def admin_render(self):
        '''Render an admin template'''
        self.render('{}.html'.format(self.view),
                    users=database.get_users(), banned_hosts=database.bans_get(),
                    sessions=api.SESSIONS, blacklist=database.blacklist_get(),
                    username=self.get_username(), view=self.view, error=self.error,
                    sysop=database.is_sysop(self.get_username()))

    def post(self):
        '''Handle POST and forward it to child classes'''
        self.set_error('')
        if not self.get_secure_cookie('logged_in'):
            self.redirect('/login?view='+self.view)
            return

        self.admin_post()

        self.admin_render()


    def get(self):
        '''Handle GET and forward it to child classes'''
        self.set_error('')
        if not self.get_secure_cookie('logged_in'):
            self.redirect('/login?view='+self.view)
            return

        self.admin_get()

        self.admin_render()

    def admin_get(self):
        '''Placeholder for classes that don't need custom GET'''

    def admin_post(self):
        '''Placeholder for classes that don't need custom POST'''
