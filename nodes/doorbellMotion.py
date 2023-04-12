#!/usr/bin/env python3
"""
Polyglot v3 - Doorbell node
Copyright (C) 2023 Universal Devices inc

MIT License
"""

from udi_interface import LOGGER, Node

'''
Doorbell motion node is a secondary node to the main Doorbell node.
'''
class DoorbellMotion(Node):
    # nodedef id
    id = 'DOORBELLMOTION'
    drivers = []

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface
        self.deviceId = ringInterface.addressToId(address)

        # REF: https://github.com/UniversalDevicesInc/hints
        #'0x01030401'
        self.hint = [1, 3, 4, 1 ]

    # When nodeserver stops, we set all devices offline
    def setOffline(self):
        self.setDriver('ST', 0)

    # DON = Motion event
    def activate(self):
        self.reportCmd('DON')

    # The commands here need to match what is in the nodedef profile file.
    commands = {}
