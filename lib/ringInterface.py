#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import time
import requests
from udi_interface import LOGGER
from lib.oauth import OAuth

# Implements the API calls to Ring
# It inherits the OAuth class
class RingInterface(OAuth):
    ringApiBasePath = 'https://api.ring.com/integrations/v1'

    def __init__(self, polyglot):
        super().__init__(polyglot)
        LOGGER.info('Ring interface initialized...')

    # The OAuth class needs to be hooked to these 3 handlers
    def customDataHandler(self, data):
        super()._customDataHandler(data)

    def customNsHandler(self, key, data):
        super()._customNsHandler(key, data)

    def oauthHandler(self, token):
        super()._oauthHandler(token)

    # Call a Ring API
    def _callApi(self, method='GET', url=None, body=None):
        # Then calling an API, get the access token (it will be refreshed if necessary)
        accessToken = self.getAccessToken()

        if accessToken is None:
            LOGGER.error('Access token is not available')
            return None

        if url is None:
            LOGGER.error('url is required')
            return None

        completeUrl = self.ringApiBasePath + url
        headers = {
            'Authorization': f"Bearer { accessToken }"
        }

        if method in [ 'PATCH', 'POST'] and body is None:
            LOGGER.error(f"body is required when using { method } with { completeUrl }")

        try:
            if method == 'GET':
                response = requests.get(completeUrl, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(completeUrl, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(completeUrl, headers=headers, json=body)
            elif method == 'POST':
                response = requests.post(completeUrl, headers=headers, json=body)
            elif method == 'PUT':
                response = requests.put(completeUrl, headers=headers)

            response.raise_for_status()
            LOGGER.info(f"Call PATCH { completeUrl } successful")
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text

        except requests.exceptions.HTTPError as error:
            LOGGER.error(f"Call PATCH { completeUrl } failed: { error }")
            return None

    def getAllDevices(self):
        return self._callApi(url='/devices')

    def getDeviceData(self, id, prefetched=None):
        if prefetched is None:
            devices = self.getAllDevices()
        else:
            devices = prefetched

        # If we don't have authorizations, devices will be null
        if not devices:
            return



    def subscribe(self, uuid, slot, pragma):
        # Our inbound events will have this pragma in the headers to make sure it's for us
        postbackUrl = f"https://dev.isy.io/api/eisy/pg3/webhook/noresponse/{ uuid }/{ slot }"

        LOGGER.info(f"Requesting subscription to { postbackUrl }")

        body = {
            'subscription': {
                'postback_url': postbackUrl,
                'metadata': {
                    'headers': {
                        'Pragma': pragma
                    }
                }
             }
        }

        return self._callApi(method='PATCH', url='/subscription', body=body)

    def unsubscribe(self):
        return self._callApi(method='DELETE', url='/subscription')

    def getUserInfo(self):
        return self._callApi(url='/user/info')

    def floodlightOn(self, deviceId):
        return self._callApi(method='PUT', url=f"/{ deviceId }/floodlight_on")

    def floodlightOff(self, deviceId):
        return self._callApi(method='PUT', url=f"/{ deviceId }/floodlight_off")
