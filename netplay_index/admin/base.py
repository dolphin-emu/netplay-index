"""Base handler that all other admin views are based on"""

from abc import abstractmethod

from tornado.web import RequestHandler

import netplay_index.database as database

# pylint: disable=W0223
class AdminHandler(RequestHandler):
    """Base handler for admin URLs"""

    @abstractmethod
    def view(self):
        """Returns the view to render"""
        raise NotImplementedError

    @abstractmethod
    def template_args(self):
        """Additional arguments needed by the template"""
        raise NotImplementedError

    def set_error(self, error):
        """Set error"""
        self.error = error

    def get_username(self):
        """Get current username or None"""
        username = self.get_secure_cookie("logged_in")

        if username is None:
            return None

        return username.decode("UTF-8")

    def admin_render(self):
        """Render an admin template"""

        ajax = self.get_argument("ajax", default=False)

        template_args = {
            "username": self.get_username(),
            "view": self.view(),
            "error": self.error,
            "sysop": database.is_sysop(self.get_username()),
            "ajax": ajax,
        }

        template_args.update(self.template_args())

        if self.error != "":
            self.set_status(403)

        self.render("{}.html".format(self.view()), **template_args)

    def post(self):
        """Handle POST and forward it to child classes"""
        self.set_error("")
        if not self.get_username():
            self.redirect("/login?view=" + self.view())
            return

        self.admin_post()

        self.admin_render()

    def get(self):
        """Handle GET and forward it to child classes"""
        self.set_error("")
        if not self.get_username():

            if self.get_argument("ajax", default=False):
                self.write("ERROR")
                return

            self.redirect("/login?view=" + self.view())
            return

        self.admin_get()

        self.admin_render()

    def admin_get(self):
        """Placeholder for classes that don't need custom GET"""

    def admin_post(self):
        """Placeholder for classes that don't need custom POST"""
