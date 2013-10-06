from gardenpath.gardener import Gardener
from twisted.internet.task import react

from twisted.python import usage

import pprint

import sys

class Options(usage.Options):
    synopsis = 'Usage: lookup.py URL'

    def parseArgs(self, url):
        self['url'] = url

def main(reactor, *argv):
    
    options = Options()
    try:
        options.parseOptions(argv)
    except usage.UsageError as errortext:
        sys.stderr.write(str(options) + '\n')
        sys.stderr.write('ERROR: %s\n' % (errortext,))
        raise SystemExit(1)

    d = Gardener().get_url(options['url'])
    d.addCallback(lambda path: pprint.pprint(path))
    d.addErrback(lambda error: pprint.pprint(error.value))
    return d
    
if __name__ == '__main__':
    react(main, sys.argv[1:])    