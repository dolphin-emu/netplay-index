import unittest

import tornado.testing

import netplay_index.tests.api as admin
import netplay_index.tests.api as api
import netplay_index.tests.redirect as redirect

TEST_MODULES = [
    "netplay_index.tests.test_admin",
    "netplay_index.tests.test_api",
    "netplay_index.tests.test_database",
    "netplay_index.tests.test_metrics",
    "netplay_index.tests.test_redirect",
]


def all():
    redirect.RedirectTest()
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


if __name__ == "__main__":
    tornado.testing.main()
