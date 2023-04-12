#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import requests
from udi_interface import LOGGER, Node
from nodes.doorbell import Doorbell

class Controller(Node):
    # nodedef id
    id = 'CTL'

    drivers = [
        { 'driver': 'ST', 'value': 0, 'uom': 2 }
    ]

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface

        polyglot.addNode(self, conn_status='ST')

        LOGGER.info('Controller Initialized...')

    def discoverDevices(self, param=None):
        userInfo = self.ring.getUserInfo()
        self.userId = userInfo['user']['id']

        LOGGER.info(f"User id is: { self.userId }")

        self.devices = self.ring.getAllDevices()
        LOGGER.info(f'Devices: { self.devices }')

        for doorbellData in self.devices['doorbells']:
            ownerId = doorbellData['owner']['id']

            if ownerId == self.userId:
                LOGGER.warn(f"Adding doorbell { doorbellData['id'] }: { doorbellData['description'] }")
                addressDoorbell = str(doorbellData['id'])
                name = doorbellData['description']
                doorbell = Doorbell(self.poly, self.address, addressDoorbell, name, self.ring)
                self.poly.addNode(doorbell)
            else:
                LOGGER.warn(f"Adding doorbell { doorbellData['id'] } ({ doorbellData['description'] }) ignored: Doorbell is shared")

    # When node is added, automatically "query" using prefetched devices data from discoverDevices
    def addNodeDoneHandler(self, nodeData):
        address = nodeData['address']

        for node in self.poly.nodes():
            if node.address == address and hasattr(node, 'queryWithPrefetched'):
                node.queryWithPrefetched(self.devices)

    def queryAll(self, param=None):
        # Prefetch devices data
        self.devices = self.ring.getAllDevices()
        LOGGER.info(f'Devices: { self.devices }')

        for node in self.poly.nodes():
            if hasattr(node, 'queryWithPrefetched'):
                # Run a query on all devices with prefetched data
                node.queryWithPrefetched(self.devices)

    # The commands here need to match what is in the nodedef profile file.
    commands = {
        'DISCOVER': discoverDevices,
        'QUERYALL': queryAll
        }


