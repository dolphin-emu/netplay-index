'''Overview page, just showing a list of other pages at the moment'''

from admin.base import AdminHandler

# pylint: disable=W0223
class Handler(AdminHandler):
    '''Handle admin overview'''
    def initialize(self):
        '''Set view name'''
        self.set_view("overview")
