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
from udi_interface import LOGGER, Custom, Interface
from lib.ringInterface import RingInterface
from nodes.controller import Controller

validEvents = [ 'new-ding', 'new-motion' ]
# Event 'new-on_demand' is sent when someone uses Live view


polyglot = None
ringInterface = None
controller = None
currentPragma = None

def configDoneHandler():
    polyglot.Notices.clear()

    accessToken = ringInterface.getAccessToken()

    if accessToken is None:
        LOGGER.info('Access token is not yet available. Please authenticate.')
        polyglot.Notices['auth'] = 'Please initiate authentication'
        return

    controller.discoverDevices()
    resubscribe()

def oauthHandler(token):
    # When user just authorized, the ringInterface needs to store the tokens
    ringInterface.oauthHandler(token)

    # Then proceed with device discovery
    configDoneHandler()

def resubscribe():
    global currentPragma

    config = polyglot.getConfig()

    # Set a new pragma. Webhooks will be accepted only if it has a header 'pragma' = currentPragma
    # We change it every long polls as a security measure
    currentPragma = str(time.time())

    LOGGER.info(f"Pragma set to { currentPragma }")

    ringInterface.subscribe(config['uuid'], config['profileNum'], currentPragma)

def pollHandler(pollType):
    if pollType == 'longPoll':
        resubscribe()
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
    pragma = data['headers']['pragma']

    # Ignore webhooks if they don't have the right pragma
    if pragma != currentPragma:
        LOGGER.info(f"Expected pragma { currentPragma }, receivedPragma { pragma }: Webhook is ignored.")
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

    LOGGER.info(f"Event { event } for address { address } ({ deviceName })")

    node = polyglot.getNode(address)

    if node is not None:
        node.activate()
    else:
        LOGGER.info(f"Node { address } not found")


if __name__ == "__main__":
    try:
        polyglot = Interface([])
        polyglot.start({ 'version': '1.0.0', 'requestId': True })

        parameters = Custom(polyglot, 'customparams')

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
