import pprint

from gardenpath.gardener import Gardener

from twisted.internet import reactor

from twisted.internet.error import ConnectionLost

import csv 

if __name__ == '__main__':

    CONNECTION_LOST_MAX = 3

    f = open('etc/top-1m.csv', 'rb')
    reader = csv.reader(f, delimiter=',')
    
    #for x in range(500225):
    #    reader.next()

    def print_headers(hl, name):       
        print '    ', name
        pprint.pprint(hl)
            
    def error_header(error, name, number, domain, error_count):
        print 'err message', error        
        if error.check(ConnectionLost) and error_count < CONNECTION_LOST_MAX:
            print 'another shot'
            new_error_count = error_count + 1
            return perform(domain, name, number, new_error_count)
        
    def perform(am, url, name, number, error_count = 0):        
        r = am.get_url(url)
        r.addCallback(print_headers, name)        
        r.addErrback(error_header, name, number, url, error_count)
        return r                        
            
    def loop(name, am):
        try:
            rn = reader.next()        
            print '', name, 'number', rn[0], 'url', rn[1]
            r = perform(am, rn[1], name, rn[0]) 
            r.addBoth(lambda ign: loop(name, am))
        except Exception as e:
            print 'LOOP EXCEPTION', e

    def launch(howmany):        
        print 'launch' + str(howmany)            
        if howmany > 0:
            loop('test' + str(howmany), Gardener())
            reactor.callLater(1, lambda: launch(howmany - 1))
        elif howmany == 0:
            print 'done!'
            
    reactor.callLater(0, launch, 30)
    reactor.run()