'''All admin interface logic resides here'''

from tornado.web import RequestHandler

import api
import database

ADMIN_VIEWS = ['admin', 'server_list', 'user_management', 'blacklist', 'bans']

# pylint: disable=W0223
class Handler(RequestHandler):
    '''Handler for admin interface stuff'''
    def do_action(self, action, user):
        '''Handle actions'''
        if action == 'change_password':
            affected_username = self.get_argument('username', None)
            password = self.get_argument('password', None)

            if not affected_username or not password:
                return 'Missing parameters'

            if user != affected_username and not database.is_sysop(user):
                return 'Only sysop can change other users passwords'

            if not database.login_exists(affected_username):
                return 'No such user'

            if not password:
                return 'Password cannot be empty!'

            database.update_login(affected_username, password)
            return ''

        if action == 'delete_user':
            affected_username = self.get_argument('username', default=None)

            if not affected_username:
                return 'Missing parameters'

            if not database.is_sysop(user):
                return 'Only sysop can delete users'

            if not database.login_exists(affected_username):
                return 'No such user'

            if user == affected_username:
                return "Can't delete own account!"

            database.delete_login(affected_username)
            return ''

        if action == 'create_user':

            affected_username = self.get_argument('username', default=None)
            password = self.get_argument('password', default=None)
            sysop = self.get_argument('sysop', default=False)
            can_ban = self.get_argument('can_ban', default=False)
            can_modify_blacklist = self.get_argument('can_modify_blacklist', default=False)

            if not affected_username and not password:
                return 'Missing parameters'

            if not database.is_sysop(user):
                return 'Only sysop can delete users'

            if database.login_exists(affected_username):
                return 'User already exists'

            if not password:
                return 'Password cannot be empty!'

            database.add_login(affected_username, password, sysop, can_ban, can_modify_blacklist)
            return ''

        if action == 'blacklist_add':
            if not database.can_modify_backlist(user):
                return 'Lacking permissions'

            word = self.get_argument('word', default=None)
            reason = self.get_argument('reason', default=None)

            if not word or not reason:
                return 'Missing parameters'

            database.blacklist_add(word, user, reason)
            return ''

        if action == 'blacklist_remove':
            if not database.can_modify_backlist(user):
                return 'Lacking permissions'

            word = self.get_argument('word', default=None)

            if not word:
                return 'Missing parameters'

            database.blacklist_remove(word)
            return ''

        if action == 'ban_add':
            if not database.can_ban(user):
                return 'Lacking permissions'

            host = self.get_argument('host', default=None)
            reason = self.get_argument('reason', default=None)

            if not host or not reason:
                return 'Missing parameters'

            database.ban_add(host, user, reason)
            return ''

        if action == 'ban_remove':
            if not database.can_ban(user):
                return 'Lacking permissions'

            host = self.get_argument('host', default=None)

            if not host:
                return 'Missing parameters'

            database.ban_remove(host)
            return ''

        return 'Bad action'

    def get(self):
        '''Handle pages'''
        view = self.get_argument('view', default='admin', strip=True)
        error = ''

        if not self.get_secure_cookie('logged_in'):
            self.redirect('/login?view='+view)
            return

        if view not in ADMIN_VIEWS:
            view = 'admin'
            error = 'No such view'

        username = self.decode_argument(self.get_secure_cookie('logged_in'))

        self.render('views/admin/{}.html'.format(view),
                    users=database.get_users(), banned_hosts=database.bans_get(),
                    blacklist=database.blacklist_get(), username=username, view=view,
                    sessions=api.SESSIONS, hosts=api.HOSTS, error=error)

    def post(self):
        '''Handle POST requests'''
        view = self.get_argument('view', default='admin', strip=True)
        action = self.get_argument('action', default=None, strip=True)

        error = ''

        if not self.get_secure_cookie('logged_in'):
            self.redirect('/login')
            return

        username = self.decode_argument(self.get_secure_cookie('logged_in'))

        if action is not None:
            error = self.do_action(action, username)

        if view not in ADMIN_VIEWS:
            view = 'admin'
            error = 'No such view'

        self.render('views/admin/{}.html'.format(view),
                    users=database.get_users(), banned_hosts=database.bans_get(),
                    blacklist=database.blacklist_get(), username=username, view=view, error=error)
