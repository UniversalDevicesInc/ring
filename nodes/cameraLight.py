#!/usr/bin/env python3
"""
Polyglot v3 - Camera lighting node
Copyright (C) 2023 Universal Devices inc

MIT License
"""

from udi_interface import LOGGER, Node

'''
Camera lighting node.
This is a secondary node to a Camera node
'''
class CameraLight(Node):
    # nodedef id
    id = 'LIGHT'
    drivers = []

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface
        self.deviceId = ringInterface.addressToId(address)

        # REF: https://github.com/UniversalDevicesInc/hints
        #'0x01021001'
        self.hint = [ 1, 2, 16, 1 ]  # Non-dimming light

    def don(self, param=None):
        LOGGER.info(f'DON received for device: { self.address }')
        self.ring.floodlightOn(self.deviceId)

    def dof(self, param=None):
        LOGGER.info(f'DOF received for device: { self.address }')
        self.ring.floodlightOff(self.deviceId)

    # The commands here need to match what is in the nodedef profile file.
    commands = {
        'DON': don,
        'DOF': dof
        }
