#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import sys
import json
import requests
from udi_interface import LOGGER, Node
from nodes.doorbell import Doorbell

class Controller(Node):
    # nodedef id
    id = 'CTL'

    drivers = [
        { 'driver': 'ST', 'value': 1, 'uom': 2 }
    ]

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface

        polyglot.addNode(self, conn_status='ST')

        LOGGER.info('Controller Initialized...')

    '''
    Read the user entered custom parameters.  Here is where the user will
    configure the number of child nodes that they want created.
    '''
#     def customParamsHandler(self, params):
#         global parameters
#         global polyglot

#         self.customParams.load(params)
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


    def discoverDevices(self):
        devices = self.ring.getAllDevices()
        LOGGER.info(f'Devices: { type(devices) } {devices}')
        LOGGER.info(f"controller address { self.address }")

        for doorbellData in devices['doorbells']:
            LOGGER.info(f"Doorbell { doorbellData['id'] }: { doorbellData['description'] }")
            address = str(doorbellData['id'])
            name = doorbellData['description']
            doorbell = Doorbell(self.poly, self.address, address, name)
            self.poly.addNode(doorbell)

    def discoverCommand(self, param):
        LOGGER.info(f'Discover not implemented param: {param}')

    # The commands here need to match what is in the nodedef profile file.
    commands = {'DISCOVER': discoverCommand }


