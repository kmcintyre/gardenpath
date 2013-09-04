from gardenpath.gardener import Gardener
from twisted.internet import reactor
import pprint
 
def example():
    d = Gardener(verbose = True).get_url('google.com')
    d.addCallback(lambda path: pprint.pprint(path))
    d.addErrback(lambda error: pprint.pprint(error.value))
    d.addBoth(lambda ign: reactor.stop())
    
reactor.callWhenRunning(example)
reactor.run()