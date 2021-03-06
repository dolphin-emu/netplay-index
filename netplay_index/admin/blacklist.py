"""Blacklist"""

from netplay_index.admin.base import AdminHandler
import netplay_index.database as database

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
        word = self.get_argument("word", default=None)
        user = self.get_username()

        if not database.can_modify_blacklist(user):
            self.set_error("Lacking permissions")
            return

        if not word:
            self.set_error("Missing parameters")
            return

        if action == "blacklist_add":
            reason = self.get_argument("reason", default=None)

            if not reason:
                self.set_error("Missing parameters")
                return

            if database.is_string_blacklisted(word):
                self.set_error("Word is already blacklisted")
                return

            database.blacklist_add(word, user, reason)
            return

        if action == "blacklist_remove":
            database.blacklist_remove(word)
