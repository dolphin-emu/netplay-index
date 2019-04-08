import unittest

import tornado.testing

import netplay_index.tests.redirect as redirect
import netplay_index.tests.api as api

TEST_MODULES = ["netplay_index.tests.redirect", "netplay_index.tests.api"]


def all():
    redirect.RedirectTest()
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


if __name__ == "__main__":
    tornado.testing.main()
