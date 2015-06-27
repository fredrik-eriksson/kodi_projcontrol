import twisted.internet as ti
import simplejson

import lib.commands

from twisted.web import server, resource


class ResourceRoot(resource.Resource):
    """Twisted resource for /"""
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        """Return the valid subcommands"""
        request.responseHeaders.addRawHeader(
                'content-type',
                'application/json'
                )
        return simplejson.dumps([ "power", "source"])

class ResourcePower(resource.Resource):
    """Twisted resource for /power"""
    isLeaf=True

    def render_GET(self, request):
        """Return a report of current projector status"""
        request.responseHeaders.addRawHeader(
                'content-type',
                'application/json'
                )
        return simplejson.dumps(lib.commands.report())

    def render_POST(self, request):
        """Set power status, valid values is "on" or "off" """
        request.responseHeaders.addRawHeader(
                'content-type',
                'application/json'
                )
        data = request.content.getvalue()
        try:
            obj = simplejson.loads(data)
        except simplejson.scanner.JSONDecodeError as err:
            return simplejson.dumps(False)

        if obj == "on":
            lib.commands.start()
            return simplejson.dumps(True)
        elif obj == "off":
            lib.commands.stop()
            return simplejson.dumps(True)

        return simplejson.dumps(False)

class ResourceSource(resource.Resource):
    """Twisted resource for /source"""
    isLeaf=True

    def render_GET(self, request):
        """Return all valid sources"""
        request.responseHeaders.addRawHeader(
                'content-type',
                'application/json'
                )
        return simplejson.dumps(lib.commands.get_available_sources())

    def render_POST(self, request):
        """Set input source, valid values can be inspected by running GET on
        /source
        """
        request.responseHeaders.addRawHeader(
                'content-type',
                'application/json'
                )
        data = request.content.getvalue()
        try:
            obj = simplejson.loads(data)
        except simplejson.scanner.JSONDecodeError as err:
            return simplejson.dumps(False)

        valid_sources = lib.commands.get_available_sources()
        if not obj in valid_sources:
            return simplejson.dumps(False)
        
        return simplejson.dumps(lib.commands.set_source(obj))


def init_server(port, address):
    """Start the twisted web server.
    
    :param port: port to listen on
    :param address: address to bind to
    """
    root = ResourceRoot()
    root.putChild('power', ResourcePower())
    root.putChild('source', ResourceSource())
    site = server.Site(root)
    ti.reactor.listenTCP(port, site, interface=address)
    ti.reactor.run(installSignalHandlers=0)


def stop_server():
    """Stop the twisted web server"""
    ti.reactor.stop()

