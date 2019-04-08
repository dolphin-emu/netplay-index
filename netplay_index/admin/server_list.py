"""List of servers"""

from netplay_index.admin.base import AdminHandler
import netplay_index.sessions as sessions

# pylint: disable=W0223
class Handler(AdminHandler):
    def template_args(self):
        """Return additional template args"""
        return {
            "sessions": sessions.get_all(),
            "hosts": sessions.hosts(),
            "regions": sessions.regions(),
        }

    """Server list handler"""

    def view(self):
        """Return view to use"""
        return "server_list"

    def admin_post(self):
        action = self.get_argument("action", default=None)
        secret = self.get_argument("secret", default=None)

        if action != "session_remove":
            return

        if secret is None:
            self.set_error("Missing parameters")
            return

        if secret in sessions.get_all():
            sessions.remove_entry(secret)
