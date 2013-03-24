gardenpath
==========

python twisted based URL auditing tool

This inspiration behind this utility is to be able to build a deferred stack for webkit


example:

    from gardenpath.finder import AccessManager
    from twisted.internet import reactor
    import pprint
    
    am = AccessManager()
    def example():
        d = am.get_url('google.com')
        d.addCallback(lambda path: pprint.pprint(path))
        d.addErrback(lambda error: pprint.pprint(error.value))
        d.addBoth(lambda ign: reactor.stop())
       
    reactor.callWhenRunning(example)
    reactor.run()
