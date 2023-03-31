#!/usr/bin/env python3
"""
Polyglot v3 node server - Ring
Copyright (C) 2023 Universal Devices

MIT License
"""

# https://github.com/UniversalDevicesInc/udi_python_interface/blob/master/API.md


import sys
import time
import json
from nodes.controller import Controller
from nodes import count_child

from lib.ringInterface import RingInterface
from udi_interface import LOGGER, Custom, Interface

polyglot = None
parameters = None
controller = None
oauth = None
n_queue = []


'''
node_queue() and wait_for_node_event() create a simple way to wait
for a node to be created.  The nodeAdd() API call is asynchronous and
will return before the node is fully created. Using this, we can wait
until it is fully created before we try to use it.
'''
def node_queue(data):
    global n_queue
    n_queue.append(data['address'])

def wait_for_node_done():
    global n_queue
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()


'''
Change all the child node active status drivers to false
'''
# def stop():
#     global polyglot
#
#     nodes = polyglot.getNodes()
#     for node in nodes:
#         if node == 'controller':   # but not the controller node
#             nodes[node].setDriver('ST', 0, True, True)
#
#     polyglot.stop()

'''
Read the user entered custom parameters.  Here is where the user will
configure the number of child nodes that they want created.
'''
# def parameterHandler(params):
#     global parameters
#     global polyglot
#
#     parameters.load(params)
#     validChildren = False

#     if parameters['nodes'] is not None:
#         if int(parameters['nodes']) > 0:
#             validChildren = True
#         else:
#             LOGGER.error('Invalid number of nodes {}'.format(parameters['nodes']))
#     else:
#         LOGGER.error('Missing number of node parameter')

#     if validChildren:
#         createChildren(int(parameters['nodes']))
#         polyglot.Notices.clear()
#     else:
#         polyglot.Notices['nodes'] = 'Please configure the number of child nodes to create zzz5.'

# def pollHandler(z):
#     global parameters
#     global polyglot
#
#     LOGGER.info('---> pollHandler')

# def oauthHandler(tokenData):
#     LOGGER.info('---> oauthHandler', json.dumps(tokenData))



'''
Create the children nodes.  Since this will be called anytime the
user changes the number of nodes and the new number may be less
than the previous number, we need to make sure we create the right
number of nodes.  Because this is just a simple example, we'll first
delete any existing nodes then create the number requested.
'''

def createChildren(how_many):
    global parameters
    global polyglot
    global controller

    # delete any existing nodes
    nodes = polyglot.getNodes()
    for node in nodes:
        if node != 'controller':   # but not the controller node
            polyglot.delNode(node)

    LOGGER.info('Creating {} children counters'.format(how_many))
    for i in range(0, how_many):
        address = 'child_{}'.format(i)
        title = 'Child Counter {}'.format(i)
        try:
            node = count_child.CounterNode(polyglot, controller.address, address, title)
            polyglot.addNode(node)
            wait_for_node_done()
        except Exception as e:
            LOGGER.error('Failed to create {}: {}'.format(title, e))

    #controller.setDriver('GV0', how_many, True, True)

def configDoneHandler():
    polyglot.Notices.clear()

    accessToken = ringInterface.getAccessToken()

    if accessToken is None:
        LOGGER.info('Access token is not yet available')
        polyglot.Notices['auth'] = 'Please initiate authentication'
        return

    controller.discoverDevices()


if __name__ == "__main__":
    try:
        polyglot = Interface([])
        polyglot.start()

#         parameters = Custom(polyglot, 'customparams')

        # Show the help in PG3 UI under the node's Configuration option
        polyglot.setCustomParamsDoc()

        # Update the profile files
        polyglot.updateProfile()    # Use checkProfile() instead?

        # Implements the API calls & Handles the oAuth authentication & token renewals
        ringInterface = RingInterface(polyglot)

        # Create the controller node
        controller = Controller(polyglot, 'controller', 'controller', 'Counter', ringInterface)

        # subscribe to the events we want
#         polyglot.subscribe(polyglot.POLL, pollHandler)
#         polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
#         polyglot.subscribe(polyglot.STOP, stop)
#         polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)

        # We subscribe after our nodes, so we run after if they register to the same events
        polyglot.subscribe(polyglot.CONFIGDONE, configDoneHandler)

        # We can start receive events
        polyglot.ready()

        # Just sit and wait for events
        polyglot.runForever()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)


