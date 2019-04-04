"""Blacklist"""

from admin.base import AdminHandler

import database

# pylint: disable=W0223
class Handler(AdminHandler):
    """Handle blacklist requests"""

    def view(self):
        """Set view to use"""
        return "blacklist"

    def template_args(self):
        """Additional parameters needed by the template"""
        return {"blacklist": database.blacklist_get()}

    def admin_post(self):
        """Handle actions"""

        action = self.get_argument("action", default=None)
        user = self.get_username()

        if action == "blacklist_add":
            if not database.can_modify_backlist(user):
                self.set_error("Lacking permissions")
                return

            word = self.get_argument("word", default=None)
            reason = self.get_argument("reason", default=None)

            if not word or not reason:
                self.set_error("Missing parameters")
                return

            database.blacklist_add(word, user, reason)
            return

        if action == "blacklist_remove":
            if not database.can_modify_backlist(user):
                self.set_error("Lacking permissions")
                return

            word = self.get_argument("word", default=None)

            if not word:
                self.set_error("Missing parameters")
                return

            database.blacklist_remove(word)
