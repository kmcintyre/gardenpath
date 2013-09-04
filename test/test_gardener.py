from gardenpath.gardener import Gardener

from twisted.trial import unittest
from twisted.web import resource, server
from twisted.internet import reactor

from twisted.internet.base import DelayedCall

import pprint

class GardenerResource(resource.Resource):
    
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
     
                     
class GardenerServerTest(unittest.TestCase):
    
    default_port = 8111

    def setUp(self):
        self.server = reactor.listenTCP(GardenerServerTest.default_port, server.Site(GardenerResource()))
        self.gardener = Gardener()
        #DelayedCall.debug = True
        
    def tearDown(self):
        d = self.server.stopListening()        
        d.addCallback(lambda ign: self.gardener.connection_pool.closeCachedConnections())
        return d
        
    def test_local_resource(self):        
        d = self.gardener.get_url('localhost:' + str(self.default_port) )
        d.addCallback(lambda ign: True)
        d.addErrback(lambda ign: self.fail('garden server failure'))
        return d

class GardenerTest(unittest.TestCase):

    def setUp(self):
        self.gardener = Gardener(verbose = True)
        DelayedCall.debug = True
        
    def tearDown(self):        
        return self.gardener.connection_pool.closeCachedConnections()

    # live has a long moved around
    def test_live_com(self):
        
        d = self.gardener.get_url('live.com')
        def outcome(dump):
            #print 'dump', pprint.pprint(dump)
            pass
        def err(error):
            print 'err', pprint.pprint(error)
            self.fail('gardener failure')
                                    
        d.addCallback(outcome)
        d.addErrback(err)
        return d
    
    
    def test_netclaim_net(self):
        #DelayedCall.debug = True
        d = self.gardener.get_url('netclaim.net')
        def outcome(dump):
            print 'dump', pprint.pprint(dump)
            return dump
        def err(error):
            print 'err', pprint.pprint(error)
            self.fail('gardener failure')
                                                
        d.addCallback(outcome)
        d.addErrback(err)
        return d
    
    def test_yieldmanager_com(self):
        
        d = self.gardener.get_url('yieldmanager.com')
        def outcome(dump):
            self.fail('gardener failure expected for yieldmanager.com')
            #print 'dump', pprint.pprint(dump)
            pass
        def err(error):
            print 'failure is success', error.value.message
            #self.fail('access manager failure', error)
            #print 'err', pprint.pprint(error)            
                        
        d.addCallback(outcome)
        d.addErrback(err)
        return d        