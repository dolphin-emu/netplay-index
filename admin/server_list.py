'''List of servers'''

from admin.base import AdminHandler

# pylint: disable=W0223
class Handler(AdminHandler):
    '''Serverlist handler'''
    def initialize(self):
        '''Set view name'''
        self.set_view("server_list")
