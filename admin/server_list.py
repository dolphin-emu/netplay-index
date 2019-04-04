'''List of servers'''

import api

from admin.base import AdminHandler

# pylint: disable=W0223
class Handler(AdminHandler):

    def template_args(self):
        '''Return additional template args'''
        return {'sessions': api.SESSIONS, 'hosts': api.HOSTS}
    
    '''Server list handler'''
    def view(self):
        '''Return view to use'''
        return 'server_list'
