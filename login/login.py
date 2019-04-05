"""Handle login logic"""

import time

from tornado.web import RequestHandler

import database
import settings

# pylint: disable=W0223
class Logout(RequestHandler):
    """Logout handler"""

    def post(self):
        """Handle logouts"""
        self.clear_cookie("logged_in")
        self.render("logout.html", ajax=False)


# pylint: disable=W0223
class Login(RequestHandler):
    """Handles login requests"""

    def get(self):
        """Handle login page"""
        if self.get_secure_cookie("logged_in"):
            view = self.get_argument("view", default="overview", strip=True)
            self.redirect("/admin/" + view)
            return

        self.render("login.html", ajax=False)

    def post(self):
        """Handle login attempts"""

        username = self.get_argument("username", default=None, strip=True)
        password = self.get_argument("password", default=None, strip=True)

        time.sleep(settings.LOGIN_ATTEMPT_DELAY)

        if database.check_login(username, password):
            self.set_secure_cookie("logged_in", username)
            view = self.get_argument("view", default="overview", strip=True)
            self.redirect("/admin/" + view)
            return

        self.render("login.html", error="Login failed.", ajax=False)
