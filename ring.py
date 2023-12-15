#!/usr/bin/env python3

"""
Polyglot v3 node server - Ring
Copyright (C) 2023 Universal Devices

MIT License
"""

# https://github.com/UniversalDevicesInc/udi_python_interface/blob/master/API.md

import sys
import json
import traceback
from udi_interface import LOGGER, Custom, Interface
from lib.ringInterface import RingInterface
from nodes.controller import Controller

validEvents = [ 'new-ding', 'new-motion', 'webhook-test' ]
# Event 'new-on_demand' is sent when someone uses Live view


polyglot = None
ringInterface = None
controller = None

def configDoneHandler():
    polyglot.Notices.clear()

    accessToken = ringInterface.getAccessToken()

    if accessToken is None:
        LOGGER.info('Access token is not yet available. Please authenticate.')
        polyglot.Notices['auth'] = 'Please initiate authentication'
        return

    controller.discoverDevices()
    ringInterface.subscribe()

def oauthHandler(token):
    # When user just authorized, the ringInterface needs to store the tokens
    ringInterface.oauthHandler(token)

    # Then proceed with device discovery
    configDoneHandler()

def pollHandler(pollType):
    if pollType == 'longPoll':
        ringInterface.subscribe()
    else:
        controller.queryAll()

def addNodeDoneHandler(node):
    # We will automatically query the device after discovery
    controller.addNodeDoneHandler(node)

def stopHandler():
    # Set nodes offline
    for node in polyglot.nodes():
        if hasattr(node, 'setOffline'):
            node.setOffline()
    polyglot.stop()

def webhookHandler(data):
    # Available information: headers, query, body
    LOGGER.debug(f"Webhook received: { data }")
    receivedPragma = data['headers']['pragma']
    currentPragma = ringInterface.getCurrentPragma()

    # Ignore webhooks if they don't have the right pragma
    if receivedPragma != currentPragma:
        LOGGER.info(f"Expected pragma { currentPragma }, receivedPragma { receivedPragma }: Webhook is ignored.")
        return

    LOGGER.info(f"Webhook body received: { data['body'] }")
    eventInfo = json.loads(data['body'])

    event = eventInfo['event'] # 'new-ding' or 'new-motion'
    id = eventInfo['data']['doorbell']['id']
    deviceName = eventInfo['data']['doorbell']['description']

    if event not in validEvents:
        LOGGER.info(f"Invalid event received: { event }")
        return

    if event == 'new-ding':
        address = str(id) + '_db'
    elif event == 'new-motion':
        address = str(id) + '_m'
    elif event == 'webhook-test':
        address = id

    LOGGER.info(f"Event { event } for address { address } ({ deviceName })")

    node = polyglot.getNode(address)

    if node is not None:
        node.activate()
    else:
        LOGGER.info(f"Node { address } not found")

if __name__ == "__main__":
    try:
        polyglot = Interface([])
        polyglot.start({ 'version': '1.1.7', 'requestId': True })

        # Show the help in PG3 UI under the node's Configuration option
        polyglot.setCustomParamsDoc()

        # Update the profile files
        polyglot.updateProfile()    # Use checkProfile() instead?

        # Implements the API calls & Handles the oAuth authentication & token renewals
        ringInterface = RingInterface(polyglot)

        # Create the controller node
        controller = Controller(polyglot, 'controller', 'controller', 'Ring', ringInterface)

        # subscribe to the events we want
        polyglot.subscribe(polyglot.POLL, pollHandler)
        polyglot.subscribe(polyglot.STOP, stopHandler)
        polyglot.subscribe(polyglot.CUSTOMDATA, ringInterface.customDataHandler)
        polyglot.subscribe(polyglot.CUSTOMNS, ringInterface.customNsHandler)
        polyglot.subscribe(polyglot.CUSTOMPARAMS, ringInterface.customParamsHandler)
        polyglot.subscribe(polyglot.OAUTH, oauthHandler)
        polyglot.subscribe(polyglot.WEBHOOK, webhookHandler)
        polyglot.subscribe(polyglot.CONFIGDONE, configDoneHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, addNodeDoneHandler)

        # We can start receive events
        polyglot.ready()

        # Just sit and wait for events
        polyglot.runForever()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

    except Exception:
        LOGGER.error(f"Error starting Ring: {traceback.format_exc()}")
        polyglot.stop()