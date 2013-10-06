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
* DNS (DNS information of hostname)

example:

python gardenpath/lookup.py google.com

	{'Alternate-Protocol': '80:quic',
	 'Cache-Control': 'private, max-age=0',
	 'Content-Type': 'text/html; charset=ISO-8859-1',
	 'Date': 'Wed, 04 Sep 2013 18:06:55 GMT',
	 'Expires': '-1',
	 'P3P': 'CP="This is not a P3P policy! See http://www.google.com/support/accounts/bin/answer.py?hl=en&answer=151657 for more info."',
	 'Reason-Phrase': 'OK',
	 'Server': 'gws',
	 'Set-Cookie': 'PREF=ID=a4dd382f952b75f0:FF=0:TM=1378318015:LM=1378318015:S=Olty-lkoIWv18ZN4; expires=Fri, 04-Sep-2015 18:06:55 GMT; path=/; domain=.google.com',
	 'Status-Code': 200,
	 'URI': 'http://www.google.com/',
	 'Version': ('HTTP', 1, 1),
	 'X-Frame-Options': 'SAMEORIGIN',
	 'X-XSS-Protection': '1; mode=block',
	 'previous': {'Alternate-Protocol': '80:quic',
	              'Cache-Control': 'public, max-age=2592000',
	              'Content-Type': 'text/html; charset=UTF-8',
	              'Date': 'Wed, 04 Sep 2013 18:06:54 GMT',
	              'Expires': 'Fri, 04 Oct 2013 18:06:54 GMT',
	              'Location': 'http://www.google.com/',
	              'Reason-Phrase': 'Moved Permanently',
	              'Server': 'gws',
	              'Status-Code': 301,
	              'URI': 'http://google.com',
	              'Version': ('HTTP', 1, 1),
	              'X-Frame-Options': 'SAMEORIGIN',
	              'X-XSS-Protection': '1; mode=block'}}