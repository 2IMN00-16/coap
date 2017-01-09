'''
Created on 08-09-2012

@author: Maciej Wasilak
'''

import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap




class CoreResource(resource.CoAPResource):
    """
    Example Resource that provides list of links hosted by a server.
    Normally it should be hosted at /.well-known/core

    Resource should be initialized with "root" resource, which can be used
    to generate the list of links.

    For the response, an option "Content-Format" is set to value 40,
    meaning "application/link-format". Without it most clients won't
    be able to automatically interpret the link format.

    Notice that self.visible is not set - that means that resource won't
    be listed in the link format it hosts.
    """

    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        print payload
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)

class Lamp (resource.CoAPResource):
    def __init__(self,lampId):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.id = lampId
        self.color = "black"
    self.addParam(resource.LinkParam("title", "Lamp"+str(lampId)))

    def render_GET(self,request):
        response = coap.Message(code=coap.CONTENT, payload=self.color)  #'%d' % (self.stat,))
        return defer.succeed(response)

    def render_PUT(self,request):
        print 'PUT payload: ' + request.payload
        payload = request.payload
        self.color = payload
        
        print 'BRIDGE CHANGE COLOR TO '+payload
        #put the code to command bridge here
        
        
        response = coap.Message(code=coap.CHANGED, payload=payload)
        return defer.succeed(response)

# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()

well_known = resource.CoAPResource()
root.putChild('.well-known', well_known)

core = CoreResource(root)
well_known.putChild('core', core)



###################

lamp0 = Lamp(0)
root.putChild('lamp0',lamp0)

lamp1 = Lamp(1)
root.putChild('lamp1',lamp1)

##################



endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
