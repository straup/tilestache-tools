#!/usr/bin/env python

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

import logging
import TileStache

def application(environ, start_response):

    config = environ['TILESTACHE_CONFIG']

    layer, coord, ext = TileStache._splitPathInfo(environ['PATH_INFO'])

    if not config.layers.get(layer, False):
        print >> environ['wsgi.errors'], "[gunistache] unknown layer: " + layer
        status = '404 NOT FOUND'
        data = ''

    else:

        try:
            content_type, data = TileStache.handleRequest(config.layers[layer], coord, ext)
            status = '200 OK'

        except Exception, e:
            print >> environ['wsgi.errors'], "[gunistache] failed to handle request:" + str(e)
            status = '500 SERVER ERROR'
            data = str(e)

    # mod_wsgi hates unicode apparently
    # so make sure everything is a str.

    response_headers = [
        ('Content-type', str(type)),
        ('Content-Length', str(len(data)))
        ]

    start_response(status, response_headers)
    return iter([data])

if __name__ == '__main__':

    import sys
    import optparse

    parser = optparse.OptionParser(usage="""httpony.py [options]""")

    parser.add_option('-c', '--config', dest='config',
                        help='The path to your TileStache config file',
                        action='store')

    parser.add_option('-P', '--port', dest='port',
                        help='The port this particular HTTP pony will run on. Default is 8000.',
                        action='store', default=8000)

    parser.add_option('-H', '--host', dest='host',
                        help='The host this particular HTTP pony will run on. Default is localhost.',
                        action='store', default='localhost')

    parser.add_option('-v', '--verbose', dest='verbose',
                        help='Enable verbose logging. Default is false.',
                        action='store_true', default=False)

    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.info('start server on %s:%s' % (options.host, options.port))

    # http://docs.python.org/library/wsgiref.html

    httpd = make_server(options.host, int(options.port), application)
    httpd.base_environ['TILESTACHE_CONFIG'] = TileStache.parseConfigfile(options.config)

    httpd.serve_forever()
