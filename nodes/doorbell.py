#!/usr/bin/env python3
"""
Polyglot v3 - Doorbell node
Copyright (C) 2023 Universal Devices inc

MIT License
"""

from udi_interface import LOGGER, Node

'''
Main Doorbell node.
Doorbell motion is implemented in a separate node DoorbellMotion.
'''
class Doorbell(Node):
    # nodedef id
    id = 'DOORBELL'
    drivers = [
        { 'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Online' },
        { 'driver': 'BATLVL', 'value': 0, 'uom': 51, 'name': 'Battery 1 percentage' },
        { 'driver': 'GV0', 'value': 0, 'uom': 51, 'name': 'Battery 2 percentage' },
        { 'driver': 'GV1', 'value': 0, 'uom': 43, 'name': 'Battery mV' }
    ]

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface
        self.deviceId = ringInterface.addressToId(address)

        # REF: https://github.com/UniversalDevicesInc/hints
        #'0x01080101'
        self.hint = [ 1, 8, 1, 1 ]

    # When nodeserver stops, we set all devices offline
    def setOffline(self):
        self.setDriver('ST', 0, True, True)

    # DON = Ding event
    def activate(self):
        self.reportCmd('DON')

    # Only nodes with this method can be globally refreshed
    def queryWithPrefetched(self, prefetched):
        self.query(prefetched)

    # Query for a single node with the possibility of passing prefetched devices data
    def query(self, prefetched=None):
        deviceData = self.ring.getDeviceData(self.deviceId, prefetched)

        LOGGER.info(f"Query for node { self.address } ({ self.name })")

        if deviceData is None:
            LOGGER.info(f"Ring device id { self.deviceId } not found")
            self.setDriver('ST', 0, True, True)
            return

        LOGGER.debug(f"Device data: { deviceData }")

        try:
            # Device is online?
            online = 1 if deviceData['alerts']['connection'] == 'online' else 0
        except KeyError:
            # If the device is not found in the devices data, mark it offline
            online = 0

        self.setDriver('ST', online, True, True, text='online')

        # Devices may have battery_life, others have battery_voltage
        try:
            bat = deviceData['battery_life']
            self.setDriver('BATLVL', bat, True, True, text='test')
        except KeyError:
            pass

        # Some devices have 2 batteries.
        try:
            bat2 = deviceData['battery_life_2']
            self.setDriver('GV0', bat2, True, True)
        except KeyError:
            pass

        try:
            batmv = deviceData['battery_voltage']
            self.setDriver('GV1', batmv, True, True)
        except KeyError:
            pass

        # Always report, even if it has not changed
        # self.reportDrivers()

    # The commands here need to match what is in the nodedef profile file.
    commands = {
        'QUERY': query
    }
