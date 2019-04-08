"""Bans"""

from netplay_index.admin.base import AdminHandler
import netplay_index.database as database

# pylint: disable=W0223
class Handler(AdminHandler):
    """Ban list"""

    def view(self):
        """Return view to use"""
        return "bans"

    def template_args(self):
        """Additional parameters needed by the template"""
        return {"banned_hosts": database.bans_get()}

    def admin_post(self):
        """Handle actions"""
        action = self.get_argument("action", default=None)
        user = self.get_username()

        if action == "ban_add":
            if not database.can_ban(user):
                self.set_error("Lacking permissions")
                return

            host = self.get_argument("host", default=None)
            reason = self.get_argument("reason", default=None)

            if not host or not reason:
                self.set_error("Missing parameters")
                return

            database.ban_add(host, user, reason)
            return

        if action == "ban_remove":
            if not database.can_ban(user):
                self.set_error("Lacking permissions")
                return

            host = self.get_argument("host", default=None)

            if not host:
                self.set_error("Missing parameters")
                return

            database.ban_remove(host)
