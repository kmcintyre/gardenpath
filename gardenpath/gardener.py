from cookielib import CookieJar

from urlparse import urljoin
from urlparse import urlparse

from twisted.web.http_headers import Headers
from twisted.web.client import Agent, CookieAgent, HTTPConnectionPool

from twisted.web.xmlrpc import XMLRPC

from twisted.internet import reactor

from twisted.python import log

import logging
import sys

class HeaderException(Exception):

    def setHeader(self, h):
        self.header = h

class TooManyHopsException(HeaderException):

    pass

class Gardener():

    HTTP_REASON_PHRASE = 'Reason-Phrase'
    HTTP_VERSION = 'Version'
    HTTP_STATUS_CODE = 'Status-Code'
    HTTP_URI = 'URI'
    DNS = 'DNS'    
    
    http_content_type = 'content-type'
    http_header_location = 'location'
    
    previous = 'previous'
    
    text_html = 'text/html'

    @staticmethod
    def get_header(headers, header):
        for h, v in headers.iteritems():
            if h.lower() == header.lower():
                return v
        return None
    
    '''
    '''        
    def __init__(self, common_headers = None, hang_up = True, use_cookies = True, pool = True, dns = True, max_hops = 5, connection_timeout = 10, verbose = False):
        if pool:
            self.connection_pool = HTTPConnectionPool(reactor, persistent=True)            
        else:
            self.connection_pool = HTTPConnectionPool(reactor, persistent=False)
            
        if use_cookies:
            cookieJar = CookieJar()
            self.agent = CookieAgent(Agent(reactor, pool = self.connection_pool), cookieJar)
        else:
            self.agent = Agent(reactor, pool = self.connection_pool)
        
        if verbose:
            log.startLogging(sys.stdout)
        
        self.hang_up = hang_up
        
        self.common_headers = common_headers
        self.max_hops = max_hops
        self.connection_timeout = connection_timeout
                
    def _request_error(self, err, url, prev = None):
        log.msg('request_error: {0} for {1}'.format(err.value.message, url), logLevel=logging.CRITICAL)            
        raise err

    def _gather_headers(self, reply, url, timer = None, prev = None):
        if timer is not None and not timer.called:
            timer.cancel()                    
        headers = {}
        if prev:
            headers[self.previous] = prev
        try:
            
            headers[self.HTTP_URI] = url
            
            for header, value in reply.headers.getAllRawHeaders():            
                headers[header] = value[0]
                        
            try:                
                headers[self.HTTP_STATUS_CODE] = reply.code
            except:
                log.msg('no code', logLevel=logging.DEBUG)
                raise Exception("Bad Response:" + url + " no " + self.HTTP_STATUS_CODE)
    
            try:
                headers[self.HTTP_VERSION] = reply.version
            except:            
                log.msg('no version', logLevel=logging.DEBUG)
                raise Exception("Bad Response:" + url + " no " + self.HTTP_VERSION)
            
            try:
                headers[self.HTTP_REASON_PHRASE] = reply.phrase
            except:
                log.msg('no phrase', logLevel=logging.DEBUG)
                raise Exception("Bad Response:" + url + " no " + self.HTTP_REASON_PHRASE)
            
            try:
                if reply._transport:
                    log.msg( 'stop producing: {0}'.format(url), logLevel=logging.DEBUG) 
                    reply._transport.stopProducing()                
                    #if reply._transport._producer:
                    #    print 'Producer', reply._transport._producer.__class__.__name__
                    #    reply._transport._producer.loseConnection()                            
            except Exception as e:
                log.msg('bad reply?: {0}'.format(e), logLevel=logging.CRITICAL)
                raise Exception("bad reply?" + url)                                    
        except Exception as e:
            he = HeaderException(e)
            he.setHeader(headers)
            raise he
        return headers

    def been_to(self, url, headers):
        if url == headers[self.HTTP_URI]:
            return True
        elif self.previous in headers:
            return self.been_to(url, headers[self.previous])
        else:
            return False
        
    def _follow_(self, headers):
        if str(headers[self.HTTP_STATUS_CODE])[:1] == '3' and Gardener.get_header(headers, self.http_header_location):
            moved_to = Gardener.get_header(headers, self.http_header_location)
            log.msg('{0} moved: {1}'.format(headers[self.HTTP_URI], moved_to), logLevel=logging.DEBUG)  
            if not urlparse(moved_to).scheme:
                moved_to = urljoin(headers[self.HTTP_URI], moved_to)
            if not self.been_to(moved_to, headers):
                log.msg('chase {0}'.format(moved_to), logLevel=logging.INFO) 
                return self.get_url(moved_to, headers)
            else:
                he = HeaderException('Code: ' + str(headers[self.HTTP_STATUS_CODE]) + ' Location and URI resolve to same:' + headers[self.HTTP_URI] + '    ' + moved_to)
                he.setHeader(headers)
                raise he
            
        elif headers[self.HTTP_STATUS_CODE] == 302 and Gardener.get_header(headers, self.http_content_type) and self.text_html in Gardener.get_header(headers, self.http_content_type):
            log.msg('acceptable 302 found', logLevel=logging.DEBUG)
            return headers
        else:
            return headers

    def timeout_request(self, timed_deferred, url):
        if not timed_deferred.called:
            log.msg('cancel request to {0}'.format(url), logLevel=logging.INFO)  
            timed_deferred.cancel()
        if timed_deferred.paused:
            def check_paused(paused_deferred):
                log.msg('paused deferred {0}'.format(paused_deferred), logLevel=logging.INFO)
                paused_deferred.cancel()
            reactor.callLater(self.connection_timeout, check_paused, timed_deferred)

    def _hang_up(self, answer, url):
        log.msg('hang up {0}'.format(self.connection_pool._connections.keys()), logLevel=logging.INFO)        
        if self.connection_pool._connections or self.connection_pool._timeouts:
            d = self.connection_pool.closeCachedConnections()
            d.addBoth(lambda ign: answer)
            return d
        else:
            log.msg('no hang up necessary: {0}'.format(url), logLevel=logging.DEBUG)
            return answer

    def get_url(self, url, prev = None):
        if not urlparse(url).scheme:
            log.msg('add http:// to {0}'.format(url), logLevel=logging.DEBUG)
            url = "http://" + url                            
        log.msg('url: {0}'.format(url), logLevel=logging.INFO)
        def previousCount(p):
            if p is None: 
                return 0
            elif self.previous in p:
                return 1 + previousCount(p[self.previous])
            else:
                return 1
        if previousCount(prev) > self.max_hops:
            log.msg('Too Many Hops {0}'.format(url), logLevel=logging.WARN) 
            ex = TooManyHopsException('Too Many Hops')
            ex.setHeader(prev)
            raise ex
                    
        request = self.agent.request('GET', url, Headers(self.common_headers))        
        
        timer = reactor.callLater(self.connection_timeout, self.timeout_request, request, url)        
        
        request.addCallback(self._gather_headers, url, timer, prev)        
        request.addCallback(self._follow_)        
        request.addErrback(self._request_error, url, prev)
        if self.hang_up and previousCount(prev) == 0:
            request.addBoth(lambda answer: self._hang_up(answer, url))
        return request

class GardenPathXMLRPCServer(Gardener, XMLRPC):        

    def __init__(self):
        XMLRPC.__init__(self, allowNone=True)        
        
    def xmlrpc_path(self, url):
        log.msg('xmlrpc_path {0}'.format(url), logLevel=logging.DEBUG)
        return self.get_url(url)