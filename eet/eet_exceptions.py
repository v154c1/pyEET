'''
Created on 15. 10. 2016

@author: neneko
'''

class BadResponse(Exception):
    def __init__(self, msg):
        super(BadResponse, self).__init__(msg)
        
class NodeNotFound(Exception):
    def __init__(self, msg):
        super(NodeNotFound, self).__init__(msg)
        