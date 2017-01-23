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

import pyhue

bridge = pyhue.Bridge("10.1.174.9","WU9GE-SxacSwEgg1S1SzWN81hlcsuVBpZf8wBOsC")

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
        #self.addParam(resource.LinkParam("title", "lamp"+str(lampId)))
        #bridge = pyhue.Bridge("192.168.0.101","WU9GE-SxacSwEgg1S1SzWN81hlcsuVBpZf8wBOsC")
        self.light = bridge.get_light(lampId)
        #self.hue = 100
        #self.bri = 100
        #self.sat = 100

    def render_GET(self,request):
        response = coap.Message(code=coap.CONTENT, payload=self.color)  #'%d' % (self.stat,))
        return defer.succeed(response)

    def render_PUT(self,request):
        print 'PUT payload: ' + request.payload
        payload = request.payload
        self.color = payload
        #########################

        index = payload.find ("=")
        #if not found, later
        attribute = payload[:index]
        value =  payload[index+1:]
        if attribute=="on":
            if value == "True":
                self.light.on = True
                print "Turn lamp "+self.id+" ON"
            else:
                self.light.on = False
                print "Turn lamp "+self.id+" OFF"

        elif attribute=="hue":
            self.light.hue = int(value)
            print "Set hue value lamp "+self.id+" to "+ value

        elif attribute=="bri":
            self.light.bri = int(value)
            print "Set brightness value lamp "+self.id+" to "+ value

        elif attribute=="sat":
            self.light.sat = int(value)
            print "Set saturation value lamp "+self.id+" to "+ value

        else:
            print "Wrong query"

        
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

lamp1 = Lamp("1")
root.putChild('lamp1',lamp1)

#lamp2 = Lamp("2")
#root.putChild('lamp2',lamp2)

#lamp3 = Lamp("3")
#root.putChild('lamp3',lamp3)
##################



endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint), interface="10.1.0.20")
reactor.run()
