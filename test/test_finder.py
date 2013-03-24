from gardenpath.finder import AccessManager

from twisted.trial import unittest
from twisted.web import resource, server
from twisted.internet import reactor

from twisted.internet.base import DelayedCall

class FinderResource(resource.Resource):
    
    isLeaf = True
    allowedMethods = ("GET")

    def request_error(self, error):
        print 'request_error', error
        raise error
    
    def render_GET(self, request):
        print 'render_GET', request.requestHeaders
        request.write( str(request.requestHeaders) ) 
        request.finish()
        return server.NOT_DONE_YET
     
                     
class FinderServerTest(unittest.TestCase):
    
    default_port = 8111

    def setUp(self):
        self.server = reactor.listenTCP(FinderServerTest.default_port, server.Site(FinderResource()))
        self.am = AccessManager()
        #DelayedCall.debug = True
    def tearDown(self):        
        d = self.server.stopListening()
        d.addCallback(lambda ign: self.am.connection_pool.closeCachedConnections())
        return d
        
    def test_local_resource(self):        
        d = self.am.get_url('localhost:' + str(self.default_port) )
        d.addCallback(lambda ign: True)
        d.addErrback(lambda ign: self.fail('access manager failure'))
        return d