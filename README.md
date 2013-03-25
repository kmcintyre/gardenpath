gardenpath
==========

python twisted based URL auditing tool for twisted 12.1 or greater

This inspiration behind this utility is to be able to build a list of deferreds for webkit.  When 
working with [QWebPage](http://qt-project.org/doc/qt-4.8/qwebpage.html) and twisted, I want to utilize 
prior knowledge (i.e. http://live.com -> http://home.live.com -> https://home.live.com -> https://mail.live.com -> 
https://login.live.com) to build a path/route of expected deferreds that fire along each step of the process 
within page.loadFinished

Hopefully it'll make it easier to answer questions - am I logged in?  was my submission valid?  
Has the host routed me based on an http request header, or cookie policy?  
   
The return value is a nested dictionary of the response headers.

I've added 4 key/value pairs:
* URI (the request url)
* Reason-Phrase (from http response)
* Status-Code (from http response)
* Version (from http response)

In addition I've added:
* previous (nested request)

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

python test/sample.py

    {'Cache-Control': 'private, max-age=0',
     'Content-Type': 'text/html; charset=ISO-8859-1',
     'Date': 'Sun, 24 Mar 2013 22:14:12 GMT',
     'Expires': '-1',
     'P3P': 'CP="This is not a P3P policy! See http://www.google.com/support/accounts/bin/answer.py?hl=en&answer=151657 for more info."',
     'Reason-Phrase': 'OK',
     'Server': 'gws',
     'Set-Cookie': 'PREF=ID=9fd3eb8661a2acfa:FF=0:TM=1364163252:LM=1364163252:S=ozhX5vEsmL9q3OjY; expires=Tue, 24-Mar-2015 22:14:12 GMT; path=/; domain=.google.com',
     'Status-Code': 200,
     'URI': 'http://www.google.com/',
     'Version': ('HTTP', 1, 1),
     'X-Frame-Options': 'SAMEORIGIN',
     'X-XSS-Protection': '1; mode=block',
     'previous': {'Cache-Control': 'public, max-age=2592000',
                  'Content-Type': 'text/html; charset=UTF-8',
                  'Date': 'Sun, 24 Mar 2013 22:14:12 GMT',
                  'Expires': 'Tue, 23 Apr 2013 22:14:12 GMT',
                  'Location': 'http://www.google.com/',
                  'Reason-Phrase': 'Moved Permanently',
                  'Server': 'gws',
                  'Status-Code': 301,
                  'URI': 'http://google.com',
                  'Version': ('HTTP', 1, 1),
                  'X-Frame-Options': 'SAMEORIGIN',
                  'X-XSS-Protection': '1; mode=block'}}

                  
imagine a list/sequence (of length 2) in page.loadFinished.connect slot and then load page. 