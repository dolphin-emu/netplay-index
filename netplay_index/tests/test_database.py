"""Checks whether the API functions properly"""

import json
import netplay_index.database as database

from unittest import TestCase


class BanTest(TestCase):
    def runTest(self):
        can_ban = database.can_ban("test_user3")
        self.assertEqual(can_ban, False)

        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc", sysop=False, can_ban_user=True)

        can_ban = database.can_ban("test_user")
        self.assertEqual(can_ban, True)

        database.delete_login("test_user")


class BlacklistTest(TestCase):
    def runTest(self):
        can_blacklist = database.can_modify_blacklist("test_user3")
        self.assertEqual(can_blacklist, False)

        if database.login_exists("test_user"):
            database.delete_login("test_user")

        database.add_login("test_user", "abc", sysop=False, can_modify_blacklist=True)

        can_blacklist = database.can_modify_blacklist("test_user")
        self.assertEqual(can_blacklist, True)

        database.delete_login("test_user")
