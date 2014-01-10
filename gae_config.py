

class GAEconfig():
    """ Keeps Google App Engine server configuration details"""
    
    def __init__(self, server_target='localhost:8080'):
        self._server = server_target

    def getServerURL(self):
        return self._server
        
    def setServerURL(self, server_target):
        print 'Running on', server_target
        self._server = server_target
        return self._server
    
    
gae_config = GAEconfig()
