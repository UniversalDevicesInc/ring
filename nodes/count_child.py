#!/usr/bin/env python3
"""
Polyglot v3 node server Example 3
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
import time
import random

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
This is our Counter device node.  All it does is update the count at the
poll interval.
'''
class CounterNode(udi_interface.Node):
    id = 'child'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 56},
            ]

    def __init__(self, polyglot, parent, address, name):
        super(CounterNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)

    '''
    Read the user entered custom parameters. In this case, it is just
    the 'multiplier' value that we want.  
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)


    '''
    This is where the real work happens.  When we get a shortPoll, increment the
    count, report the current count in GV0 and the current count multiplied by
    the user defined value in GV1. Then display a notice on the dashboard.
    '''
    def poll(self, polltype):

        if 'shortPoll' in polltype:
            if self.Parameters['multiplier'] is not None:
                mult = int(self.Parameters['multiplier'])
            else:
                mult = 1

            self.count += 1

            time.sleep(random.randrange(15))

            self.setDriver('GV0', self.count, True, True)
            time.sleep(.1)
            self.setDriver('GV1', (self.count * mult), True, True)
            time.sleep(.1)

            # be fancy and display a notice on the polyglot dashboard
            self.poly.Notices[self.name] = '{}: Current count is {}'.format(self.name, self.count)

