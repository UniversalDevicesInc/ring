#!/usr/bin/env python3
"""
Polyglot v3 node server - Ring
Copyright (C) 2023 Universal Devices

MIT License
"""

# https://github.com/UniversalDevicesInc/udi_python_interface/blob/master/API.md


import udi_interface
import sys
import time
import json
from nodes.controller import Controller
from nodes import count_child

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
parameters = None
controller = None
n_queue = []

testToken = json.loads('{"access_token": "eyJhbGciOiJSUzI1NiIsImprdSI6Ii9vYXV0aC9pbnRlcm5hbC9qd2tzIiwia2lkIjoiNGRjODQyZGIiLCJ0eXAiOiJKV1QifQ.eyJhcHBfaWQiOiJwZ3Byb2QiLCJjaWQiOiJwZ3Byb2QiLCJleHAiOjE2Nzk1MjE4MzYsImhhcmR3YXJlX2lkIjoidW5kZWZpbmVkIiwiaWF0IjoxNjc5NTE4MjM2LCJpc3MiOiJSaW5nT2F1dGhTZXJ2aWNlLXByb2Q6dXMtZWFzdC0xOjVmM2U1NTkyIiwicm5kIjoiT0ZfaTVGdTNGZSIsInNjb3BlcyI6WyJyZWFkIl0sInNlc3Npb25faWQiOiJiNDM5MGNhMi1kMjkzLTRhYTgtYTlkOC0xMWNhYTU1MjBjNDkiLCJ1c2VyX2lkIjoxOTc3MjgxfQ.jf8V2wpCZQ1-BGMqLvhVEoIxFFAfm-Lp3ictTSDYHsl0c2HhkvOSoQ50O0v6M07CRzvajw3QXHzpXnv-qubGBeZCp80-WL0S0BNxww-a1uOhmOAvkCB-3qjrBXRiKLtVvDb21HXe9cn_rmAzhpt-lltA09xWEJImpYHVPZOhmYnZEcLMvuXiwPVFO6-k2ZLMdo1b5irCQfX1Sa1Jlz1_lsxnODeCbEnpI92CiOFcJJAPoIfAMuEjW5qo8rbllWpqY-KQ4RhKBqQZqm-xhAPXc5U_PhA3bBXu1pgX5yl9wp66zbYLWl03xSM7XcWEmV02aigghopsNbYbJiFCBR98Eg", "expires_in": 3600, "refresh_token": "eyJhbGciOiJSUzI1NiIsImprdSI6Ii9vYXV0aC9pbnRlcm5hbC9qd2tzIiwia2lkIjoiNGRjODQyZGIiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE2Nzk1MTgyMzYsImlzcyI6IlJpbmdPYXV0aFNlcnZpY2UtcHJvZDp1cy1lYXN0LTE6NWYzZTU1OTIiLCJyZWZyZXNoX2NpZCI6InBncHJvZCIsInJlZnJlc2hfc2NvcGVzIjpbInJlYWQiXSwicmVmcmVzaF91c2VyX2lkIjoxOTc3MjgxLCJybmQiOiJMYmFkczBGZW5HIiwic2Vzc2lvbl9pZCI6ImI0MzkwY2EyLWQyOTMtNGFhOC1hOWQ4LTExY2FhNTUyMGM0OSIsInR5cGUiOiJyZWZyZXNoLXRva2VuIn0.c5BZFGIwOxKWi3KfiCPutNKLunA0YEgPCEztPeHhmZRgPLfeV2BDSpfzhKSRSQKAUpK6sXxmEpF6UDx_5Yr9ofDy36u2Nu7IbCiOv5BycCWLJlv90Ddfuxs7qsJsbXdH-9X9gcqiQeOFTQITnDyuft3Wmet-bzACbWIN55ZR44ZiPD-o9-uLO50fwMut7CtAg1h0m9NyhNYudL9ht1gQPeTtqoJBo6V1gE2ji65mhB3YKwz1lSUYlJoSdZ_Gi6jo2sg78Hw7N7gjOo6KzgTlaSEZAV1WYzSYZqTP_nw2EzRpWTmV-6Non-Xz6ueX_5176L7k0pwEUudO3rfW1tH1ew", "scope": "read", "token_type": "Bearer"}')


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


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

#         parameters = Custom(polyglot, 'customparams')

        # Show the help in PG3 UI under the node's Configuration option
        polyglot.setCustomParamsDoc()

        # Update the profile files
        polyglot.updateProfile()    # Use checkProfile() instead?

        # subscribe to the events we want
#         polyglot.subscribe(polyglot.POLL, pollHandler)
#         polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
#         polyglot.subscribe(polyglot.STOP, stop)
#         polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
#         polyglot.subscribe(polyglot.OAUTH, oauthHandler)

        # Create the controller node
        controller = Controller(polyglot, 'controller', 'controller', 'Counter')
#        polyglot.addNode(controller, conn_status='ST')

        # Just sit and wait for events
        polyglot.runForever()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)


