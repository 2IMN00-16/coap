'''
Created on 08-09-2012

@author: Maciej Wasilak
'''

import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

from ipaddress import ip_address

class Agent():
    """
    Example class which performs single PUT request to iot.eclipse.org
    port 5683 (official IANA assigned CoAP port), URI "/large-update".
    Request is sent 1 second after initialization.

    Payload is bigger than 64 bytes, and with default settings it
    should be sent as several blocks.
    """

    def __init__(self, protocol):
        self.protocol = protocol
        #reactor.callLater(1, self.putResource)

    def putResource(self,ip,color,lampId):
        payload = color#"purple"
        request = coap.Message(code=coap.PUT, payload=payload)
        request.opt.uri_path = (lampId,)#"lamp0",)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = (ip_address(ip), coap.COAP_PORT)
        d = protocol.request(request)
        d.addCallback(self.printResponse)

    def printResponse(self, response):
        print 'Response Code: ' + coap.responses[response.code]
        print 'Payload: ' + response.payload
        reactor.stop()

log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)
reactor.listenUDP(61616, protocol)
ip='192.168.0.103'
##########################
color = "red"
lampId = "lamp0"

client.putResource(ip,color,lampId)
client.putResource(ip,"brown",lampId)

