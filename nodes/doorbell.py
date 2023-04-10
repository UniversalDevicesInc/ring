#!/usr/bin/env python3
"""
Polyglot v3 - Doorbell node
Copyright (C) 2023 Universal Devices inc

MIT License
"""
# import udi_interface
# import sys
# import time

from udi_interface import LOGGER, Node

'''
This is our Counter device node.  All it does is update the count at the
poll interval.
'''
class Doorbell(Node):
    # nodedef id
    id = 'DOORBELL'
    drivers = [
            { 'driver': 'ST', 'value': 0, 'uom': 2 },
            { 'driver': 'BAT', 'value': 0, 'uom': 51 },
            { 'driver': 'BAT2', 'value': 0, 'uom': 51 },
            { 'driver': 'BATMV', 'value': 0, 'uom': 43 },
            { 'driver': 'ERR', 'value': 0, 'uom': 2 }
            ]

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface

#         self.Parameters = Custom(polyglot, 'customparams')

    def dingCommand(self, param):
        LOGGER.info(f'Ding not implemented param: {param}')

    def queryCommand(self, param):
        LOGGER.info(f'Query not implemented param: {param}')

    # The commands here need to match what is in the nodedef profile file.
    commands = {
        'DON': dingCommand,
        'QUERY': queryCommand
        }
