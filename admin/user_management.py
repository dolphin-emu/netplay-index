"""User Management"""
from admin.base import AdminHandler

import database

# pylint: disable=W0223
class Handler(AdminHandler):
    """User Management View"""

    def view(self):
        """Set view to use"""
        return "user_management"

    def template_args(self):
        """Additional template arguments"""
        return {"users": database.get_users()}

    def change_user_password(self, username, password):
        """Change username's password"""
        if not username or not password:
            self.set_error("Missing parameters")
            return

        if self.get_username() != username and not database.is_sysop(
            self.get_username()
        ):
            self.set_error("Only sysop can change other users passwords")
            return

        if not database.login_exists(username):
            self.set_error("No such user")
            return

        if not password:
            self.set_error("Password cannot be empty!")
            return

        database.update_login(username, password)

    def remove_user(self, username):
        """Remove user"""

        if not username:
            self.set_error("Missing parameters")
            return

        if not database.is_sysop(self.get_username()):
            self.set_error("Only sysop can delete users")
            return

        if not database.login_exists(username):
            self.set_error("No such user")
            return

        if self.get_username() == username:
            self.set_error("Can't delete own account!")
            return

        database.delete_login(username)

    def create_user(self, username, password, sysop, can_ban, can_modify_blacklist):
        if not username and not password:
            self.set_error("Missing parameters")
            return

        if not database.is_sysop(self.get_username()):
            self.set_error("Only sysop can create users")
            return

        if database.login_exists(username):
            self.set_error("User already exists")
            return

        if not password:
            self.set_error("Password cannot be empty!")
            return

        database.add_login(username, password, sysop, can_ban, can_modify_blacklist)

    def admin_post(self):
        """Handle actions"""

        action = self.get_argument("action", default=None)
        affected_username = self.get_argument("username", default=None)

        if action == "change_password":
            password = self.get_argument("password", default=None)

            self.change_user_password(affected_username, password)
            return

        if action == "delete_user":
            self.remove_user(affected_username)
            return

        if action == "create_user":
            password = self.get_argument("password", default=None)
            sysop = self.get_argument("sysop", default=False)
            can_ban = self.get_argument("can_ban", default=False)
            can_modify_blacklist = self.get_argument(
                "can_modify_blacklist", default=False
            )

            self.create_user(
                affected_username, password, sysop, can_ban, can_modify_blacklist
            )
