'''Handle API requests'''

import time

from tornado.web import RequestHandler
from util import check_origin, generate_secret, get_ip

import database

SESSIONS = {}
HOSTS = {}

LAST_SESSION_CLEANUP = 0

SESSION_CLEANUP_DELAY = 30
SESSION_TIMEOUT_SECONDS = 15

def _cleanup_sessions():
    to_delete = []
    for key in SESSIONS:
        if time.time() - SESSIONS[key]['timestamp'] > SESSION_TIMEOUT_SECONDS:
            to_delete.append(key)

    for key in to_delete:
        del SESSIONS[key]

# pylint: disable=W0223
class Handler(RequestHandler):
    '''Handler for all API requests'''
    def session_add(self):
        '''Adds a new session'''

        if not check_origin(self):
            self.write({'status': 'BAD_ORIGIN'})
            return

        session = {}
        for key in ['name', 'region', 'game', 'server_id',
                    'port', 'player_count', 'in_game', 'password']:
            session[key] = self.get_argument(key, default=None, strip=True)
            if session[key] is None:
                self.write({'status': 'MISSING_PARAMETER', 'parameter': key})
                return
            if database.is_string_blacklisted(session[key]):
                self.write({'status': 'BLACKLISTED_WORD', 'parameter': key})
                return

        secret = generate_secret()

        SESSIONS[secret] = session
        SESSIONS[secret]['timestamp'] = time.time()
        HOSTS[secret] = get_ip(self)

        self.write({'status': 'OK', 'secret': secret})

    def session_active(self):
        '''Keeps a session alive and updates some details'''
        secret = self.get_argument('secret', default=None, strip=True)
        game = self.get_argument('game', default=None, strip=True)
        in_game = self.get_argument('in_game', default=None, strip=True)

        if secret not in SESSIONS:
            self.write({'status': 'BAD_SESSION'})
            return

        SESSIONS[secret]['timestamp'] = time.time()


        if game is not None:
            if database.is_string_blacklisted(game):
                self.write({'status': 'BLACKLISTED_WORD', 'parameter': 'game'})
                return
            SESSIONS[secret]['game'] = game

        if in_game is not None:
            SESSIONS[secret]['in_game'] = in_game

        self.write({'status': 'OK'})

    def session_remove(self):
        '''Removes a session'''
        secret = self.get_argument('secret', default=None, strip=True)

        if secret not in SESSIONS:
            self.write({'status': 'BAD_SESSION'})
            return

        del SESSIONS[secret]
        del HOSTS[secret]

        self.write({'status': 'OK'})

    def list(self):
        '''List all sessions matching filter'''
        # pylint: disable=W0603
        global LAST_SESSION_CLEANUP

        if time.time() - LAST_SESSION_CLEANUP > SESSION_CLEANUP_DELAY:
            LAST_SESSION_CLEANUP = time.time()
            _cleanup_sessions()

        self.write({'status': 'OK', 'sessions': list(SESSIONS.values())})

    def get(self, api_version, action):
        '''Answer get requests'''
        api_version = int(api_version)
        if api_version != 0:
            self.write({'status': 'BAD_VERSION'})
            return

        if not check_origin(self):
            self.write({'status': 'BAD_ORIGIN'})
            return

        if database.is_host_banned(get_ip(self)):
            self.write({'status': 'IP_BANNED'})
            return

        actions = {
            'session/add': self.session_add,
            'session/remove': self.session_remove,
            'session/active': self.session_active,
            'list': self.list
        }

        if action not in actions:
            self.write({'status': 'BAD_ACTION'})
            return

        actions[action]()
