'''Database helper'''

import sqlite3
import hashlib
import re

CONNECTION = None

def _get_cursor():
    '''Returns a connection cursor'''
    return CONNECTION.cursor()

def _commit():
    '''Commit database changes'''
    CONNECTION.commit()

def _hash_password(password):
    '''Hashes a password for storing in the database'''
    return hashlib.sha256(password.encode('UTF-8')).hexdigest()

def initialize():
    '''Initialize database before usage'''

    # pylint: disable=W0603
    global CONNECTION

    CONNECTION = sqlite3.connect('main.db')

    cur = _get_cursor()

    # Initialize users
    cur.execute('''
CREATE TABLE IF NOT EXISTS users
(username TEXT PRIMARY KEY, password TEXT, sysop BOOL, can_ban BOOL,
 can_modify_blacklist BOOL)''')

    # Initialize blacklist
    cur.execute('''
CREATE TABLE IF NOT EXISTS bans

(host TEXT PRIMARY KEY, date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
 added_by TEXT, reason TEXT)''')

    # Initialize ban list
    cur.execute('''
CREATE TABLE IF NOT EXISTS blacklist
(word TEXT PRIMARY KEY, date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
 added_by TEXT, reason TEXT)
''')

    print('Initialized database successfully.')

    return True

def add_login(username, password, sysop=False, can_ban_user=False, can_modify_blacklist=False):
    '''Add user'''
    cur = _get_cursor()

    cur.execute('''INSERT INTO users
(username, password, sysop, can_ban, can_modify_blacklist)
VALUES (?, ?, ?, ?, ?)''',

                (username, _hash_password(password), sysop, can_ban_user, can_modify_blacklist))

    _commit()

def update_login(username, password):
    '''Change login information'''
    cur = _get_cursor()
    cur.execute('''
UPDATE users SET password = ? WHERE username = ?''',
                (_hash_password(password), username))

    _commit()

def is_sysop(username):
    '''Checks whether a user is sysop'''

    cur = _get_cursor()

    cur.execute('SELECT sysop FROM users WHERE username=?', [username])

    value = cur.fetchone()

    if value is None:
        return False

    return value

def can_ban(username):
    '''Check whether a user can ban hosts'''

    if is_sysop(username):
        return True

    cur = _get_cursor()

    cur.execute('SELECT can_ban FROM users WHERE username=?', [username])

    value = cur.fetchone()

    if value is None:
        return False

    return value[0]

def can_modify_backlist(username):
    '''Checks whether a user can modify a blacklist'''

    if is_sysop(username):
        return True

    cur = _get_cursor()

    cur.execute('SELECT can_modify_blacklist FROM users WHERE username=?', [username])

    value = cur.fetchone()

    if value is None:
        return False

    return value

def delete_login(username):
    '''Remove user'''
    cur = _get_cursor()

    cur.execute('DELETE FROM users WHERE username=?', [username])
    _commit()

def login_exists(username):
    '''Check whether a user exists'''
    cur = _get_cursor()

    cur.execute('SELECT password FROM users WHERE username=?', [username])

    value = cur.fetchone()

    return value is not None

def check_login(username, password):
    '''Check whether a given username and password pair is valid'''
    cur = _get_cursor()

    cur.execute('SELECT password FROM users WHERE username=?', [username])

    hashed_password = cur.fetchone()

    if hashed_password is None:
        print("Attempted login for non-existent user '{}'".format(username))
        return False

    hashed_password = hashed_password[0]

    return _hash_password(password) == hashed_password

def get_users():
    '''Get all users'''
    cur = _get_cursor()

    cur.execute('SELECT username, sysop, can_ban, can_modify_blacklist FROM users')

    return cur.fetchall()

def bans_get():
    '''Get all banned hosts'''
    cur = _get_cursor()

    cur.execute('SELECT host, date_added, added_by, reason FROM bans')

    return cur.fetchall()

def blacklist_get():
    '''Get all blacklisted words'''
    cur = _get_cursor()

    cur.execute('SELECT word, date_added, added_by, reason FROM blacklist')

    return cur.fetchall()

def blacklist_add(word, user, reason):
    '''Add a word to the blacklist'''
    cur = _get_cursor()

    cur.execute('''
INSERT INTO blacklist(word, added_by, reason)
VALUES (?, ?, ?)''', [word, user, reason])

    _commit()

def blacklist_remove(word):
    '''Remove word from the blacklist'''
    cur = _get_cursor()

    cur.execute('DELETE FROM blacklist WHERE word=?', [word])

    _commit()

def ban_add(host, user, reason):
    '''Add a host to the ban list'''
    cur = _get_cursor()

    cur.execute('INSERT INTO bans(host, added_by, reason) VALUES (?, ?, ?)', [host, user, reason])

    _commit()

def ban_remove(host):
    '''Remove a host from the ban list'''
    cur = _get_cursor()

    cur.execute('DELETE FROM bans WHERE host=?', [host])

    _commit()

def is_host_banned(host):
    '''Checks whether a given host is banned from using this service'''
    cur = _get_cursor()

    cur.execute('SELECT reason FROM bans WHERE host=?', [host])

    reason = cur.fetchone()

    return reason is not None

def is_string_blacklisted(string):
    '''Checks whether a string contains blacklisted words'''
    cur = _get_cursor()

    cur.execute('SELECT word FROM blacklist')

    words = cur.fetchall()

    for word in words:
        word = word[0]
        if re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search(string) is not None:
            return True

    return False
