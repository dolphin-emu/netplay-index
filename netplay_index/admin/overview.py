"""Overview page, just showing a list of other pages at the moment"""

from netplay_index.admin.base import AdminHandler
import netplay_index.sessions as sessions

# pylint: disable=W0223
class Handler(AdminHandler):
    """Handle admin overview"""

    def template_args(self):
        """Additional template arguments"""

        total_player_count = 0

        for secret in sessions.get_all():
            total_player_count += sessions.get_entry(secret)["player_count"]

        return {
            "session_count": sessions.count(),
            "total_player_count": total_player_count,
        }

    def view(self):
        """View to display"""
        return "overview"
