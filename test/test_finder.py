from gardenpath.finder import AccessManager

from twisted.trial import unittest
from twisted.web import resource, server
from twisted.internet import reactor

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
    def tearDown(self):        
        self.server.stopListening()
        
    def test_local_resource(self):     
        am = AccessManager()
        d = am.get_url('localhost:' + str(self.default_port) )
        d.addCallback(lambda ign: True)
        #d.addCallback(lambda ign: am.connection_pool.closeCachedConnections())
        d.addErrback(lambda ign: self.fail('access manager failure'))
        return d