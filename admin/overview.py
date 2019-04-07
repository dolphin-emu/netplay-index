"""Overview page, just showing a list of other pages at the moment"""

from admin.base import AdminHandler

import api

# pylint: disable=W0223
class Handler(AdminHandler):
    """Handle admin overview"""

    def template_args(self):
        """Additional template arguments"""

        total_player_count = 0

        for secret in api.SESSIONS:
            total_player_count += api.SESSIONS[secret]['player_count']

        return {
            "session_count": len(api.SESSIONS),
            "total_player_count": total_player_count
        }

    def view(self):
        """View to display"""
        return "overview"
