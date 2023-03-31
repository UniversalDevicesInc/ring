#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import udi_interface
import sys
import json
import requests
from datetime import timedelta, datetime

LOGGER = udi_interface.LOGGER

'''
Controller is interfacing with both Polyglot and the device. In this
case the device is just a count that has two values, the count and the count
multiplied by a user defined multiplier. These get updated at every
shortPoll interval.
'''
class Controller(udi_interface.Node):
    # nodedef id
    id = 'ctl'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        #{'driver': 'GV0', 'value': 0, 'uom': 56},
        ]

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface
#         self.customParams = udi_interface.Custom(polyglot, 'customparams')

        # self.customData.token contains the oAuth tokens
#         self.customData = udi_interface.Custom(polyglot, 'customdata')

        # This is the oauth configuration from the node server store
#         self.oauthConfig = {}

#         self.ringApiHost = 'https://api.ring.com'
#         self.ringApiBasePath = '/integrations/v1'

        polyglot.subscribe(polyglot.POLL, self.pollHandler)
#         polyglot.subscribe(polyglot.CUSTOMPARAMS, self.customParamsHandler)
#         polyglot.subscribe(polyglot.CUSTOMDATA, self.customDataHandler)
#         polyglot.subscribe(polyglot.CUSTOMNS, self.customNsHandler)

#        polyglot.subscribe(polyglot.STOP, stop)
#        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
#         polyglot.subscribe(polyglot.OAUTH, self.oauthHandler)
#         polyglot.subscribe(polyglot.CONFIGDONE, self.configDoneHandler)

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

#     def customDataHandler(self, data):
#         LOGGER.debug('Received customData: {}'.format(json.dumps(data)))
#         self.customData.load(data)

#     def customNsHandler(self, key, data):
#         # LOGGER.info('CustomNsHandler {}'.format(key))
#         if key == 'oauth':
#             LOGGER.debug('CustomNsHandler oAuth: {}'.format(json.dumps(data)))
#
#             self.oauthConfig = data
#
#             if self.oauthConfig.get('auth_endpoint') is None:
#                 LOGGER.error('oAuth configuration is missing auth_endpoint')
#
#             if self.oauthConfig.get('token_endpoint') is None:
#                 LOGGER.error('oAuth configuration is missing token_endpoint')
#
#             if self.oauthConfig.get('client_id') is None:
#                 LOGGER.error('oAuth configuration is missing client_id')
#
#             if self.oauthConfig.get('client_secret') is None:
#                 LOGGER.error('oAuth configuration is missing client_secret')

#     def configDoneHandler(self):
#         self.poly.Notices.clear()
#
#         token = self.customData['token']
#
#         if token is None:
#             LOGGER.debug('Token is not set')
#             self.poly.Notices['auth'] = 'Please initiate authentication'
#             return
#
#         self.oAuthTokensEnsureRefresh()
#         self.discoverDevices()

    def pollHandler(self, z):
        LOGGER.info('---> pollHandler')

    '''
    User proceeded through oAuth authentication.
    The authorization_code has already been exchanged for access_token and refresh_token by PG3
    '''
#     def oauthHandler(self, token):
#         LOGGER.info('-------------------------- Authenticate ---------------------------------')
#         LOGGER.info('Authentication to Ring completed')
#         LOGGER.debug('Received oAuth tokens: {}'.format(json.dumps(token)))
#         self.saveToken(token)

#     def saveToken(self, token):
#         # Add the expiry key, so that we can later check if the tokens are due to be expired
#         token['expiry'] = (datetime.now() + timedelta(seconds=token['expires_in'])).isoformat()
#
#         # This updates our copy of customData, but also sends it to PG3 for storage
#         self.customData['token'] = token

    '''
    Refresh oAuth tokens if necessary
    '''
#     def oAuthTokensEnsureRefresh(self):
#         token = self.customData.token
#         expiry = token.get('expiry')
#
#         # If expired or expiring in less than 60 seconds, refresh
#         if expiry is None or datetime.fromisoformat(expiry) - timedelta(seconds=60) < datetime.now():
#             LOGGER.info('Refresh tokens expired. Initiating refresh.')
# #             LOGGER.info('Original tokens: {}'.format(json.dumps(token)))
#             self.oAuthTokensRefresh()
#         else:
#             LOGGER.info('Refresh tokens is still valid, no need to refresh')

#     def oAuthTokensRefresh(self):
#         LOGGER.info('-------------------------- Refreshing oAuth tokens ---------------------------------')
#         LOGGER.info(f'Token before [{ type(self.customData.token) }]: { self.customData.token }')
#         data = {
#             'grant_type': 'refresh_token',
#             'refresh_token': self.customData.token['refresh_token'],
#             'client_id': self.oauthConfig['client_id'],
#             'client_secret': self.oauthConfig['client_secret']
#         }
#         LOGGER.info(f'Token refresh data: { data }')
#         LOGGER.info(f'oauthConfig: { self.oauthConfig }')
#         try:
#             response = requests.post(self.oauthConfig['token_endpoint'], data=data)
#             response.raise_for_status()
#             token = response.json()
#             LOGGER.info('Refreshing oAuth tokens successful')
#             LOGGER.debug(f'Token refresh result [{ type(token) }]: { token }')
#             self.saveToken(token)
#
#         except requests.exceptions.HTTPError as error:
#             LOGGER.info(f'Failed to refresh oAuth token: { error }')

#     def callApiGet(self, url):
#         self.oAuthTokensEnsureRefresh()
#         completeUrl = self.ringApiHost + self.ringApiBasePath + url
#         headers = {
#             "Authorization": f"Bearer {self.customData.token['access_token']}"
#         }
#         try:
#             response = requests.get(completeUrl, headers=headers)
#             response.raise_for_status()
#             LOGGER.info(f'Call GET { completeUrl } successful')
#             return response.json()
#
#         except requests.exceptions.HTTPError as error:
#             LOGGER.error(f'Call GET { completeUrl } failed: { error }')

    def discoverDevices(self):
        devices = self.ring.getAllDevices()
        LOGGER.info(f'Devices: { type(devices) } {devices}')

    def discoverCommand(self, param):
        LOGGER.info(f'Discover not implemented param: {param}')

    '''
    The commands here need to match what is in the nodedef profile file.
    '''
    commands = {'DISCOVER': discoverCommand }

