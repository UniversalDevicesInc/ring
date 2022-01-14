#!/usr/bin/env python3
"""
Polyglot v3 node server Example 2
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
import time
from nodes import count_ctl
from nodes import count_child

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
parameters = None
controller = None
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
def stop():
    global polyglot

    nodes = polyglot.getNodes()
    for node in nodes:
        if node != 'controller':   # but not the controller node
            nodes[node].setDriver('ST', 0, True, True)

    polyglot.stop()

'''
Read the user entered custom parameters.  Here is where the user will
configure the number of child nodes that they want created.
'''
def parameterHandler(params):
    global parameters
    global polyglot

    parameters.load(params)
    validChildren = False

    if parameters['nodes'] is not None:
        if int(parameters['nodes']) > 0:
            validChildren = True
        else:
            LOGGER.error('Invalid number of nodes {}'.format(parameters['nodes']))
    else:
        LOGGER.error('Missing number of node parameter')


    if validChildren:
        createChildren(int(parameters['nodes']))
        polyglot.Notices.clear()
    else:
        polyglot.Notices['nodes'] = 'Please configure the number of child nodes to create.'


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

    controller.setDriver('GV0', how_many, True, True)


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.STOP, stop)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)

        polyglot.ready()

        # Create the controller node
        controller = count_ctl.Controller(polyglot, 'controller', 'controller', 'Counter')
        polyglot.addNode(controller, conn_status='ST')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

