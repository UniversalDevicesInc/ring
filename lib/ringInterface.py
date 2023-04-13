#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import time
import re
import requests
from udi_interface import LOGGER
from lib.oauth import OAuth

# Implements the API calls to Ring
# It inherits the OAuth class
class RingInterface(OAuth):
    ringApiBasePath = 'https://api.ring.com/integrations/v1'

    def __init__(self, polyglot):
        super().__init__(polyglot)

        self.poly = polyglot
        LOGGER.info('Ring interface initialized...')

    # The OAuth class needs to be hooked to these 3 handlers
    def customDataHandler(self, data):
        super()._customDataHandler(data)

    def customNsHandler(self, key, data):
        super()._customNsHandler(key, data)

    def oauthHandler(self, token):
        super()._oauthHandler(token)

    # Convert nodeserver address to a ring device id (Strip non-numeric characters)
    def addressToId(self, address):
        return int(re.sub(r"[^\d]+", '', address))

    def getPostbackUrl(self, uuid, slot):
        return f"https://dev.isy.io/api/eisy/pg3/webhook/noresponse/{ uuid }/{ slot }"

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

        #LOGGER.info(f"completeUrl { completeUrl }")
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
            LOGGER.error(f"Call { method } { completeUrl } failed: { error }")
            return None

    # Call a Ring API to test connectivity
    def testApiCall(self):
        # Then calling an API, get the access token (it will be refreshed if necessary)
        accessToken = self.getAccessToken()

        if accessToken is None:
            raise Exception('Access token is not available')

        completeUrl = self.ringApiBasePath + '/user/info'

        headers = {
            'Authorization': f"Bearer { accessToken }"
        }

        try:
            response = requests.get(completeUrl, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            LOGGER.error(f"Call GET { completeUrl } failed: { error }")
            raise Exception('Connection to Ring API failed')

    def testWebhook(self, body):
        try:
            config = self.poly.getConfig()
            completeUrl = self.getPostbackUrl(config['uuid'], config['profileNum'])

            headers = {
                'pragma': self.currentPragma
            }

            response = requests.post(completeUrl, headers=headers, json=body, timeout=5)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            httpStatus = error.response.status_code

            # Not online?
            if httpStatus == 503:
                LOGGER.error(f"MQTT connection not online.\nOn my.isy.io, please check Select Tool | Maintenance | PG3 Remote connection. It has to be active.\nIf you don't see the option, your device does not support it. Make sure you are using an eisy at 5.5.9 or more recent, or a Polisy using PG3x.")
            # No access to uuid?
            elif httpStatus == 423:
                LOGGER.error(f"Make sure that uuid { config['uuid'] } is in your portal account, has a license and is authorized.")
            else:
                LOGGER.error(f"Call event url failed GET { completeUrl } failed with HTTP { httpStatus }: { error }")

            raise Exception('Error sending event to Portal webhook')

    def getAllDevices(self):
        return self._callApi(url='/devices')

    def getDeviceData(self, id, prefetched=None):
        if prefetched is None:
            LOGGER.info('prefetched is none')
            devices = self.getAllDevices()
        else:
            devices = prefetched

        # If we don't have authorizations, devices will be null
        if devices is None:
            return

        allDevices = devices['doorbells'] + devices['stickup_cams']
        return next((d for d in allDevices if d['id'] == id), None)

    def subscribe(self):
        config = self.poly.getConfig()
        postbackUrl = self.getPostbackUrl(config['uuid'], config['profileNum'])

        # Set a new pragma. Webhooks will be accepted only if it has a header 'pragma' = currentPragma
        # We change it every long polls as a security measure
        self.currentPragma = str(time.time())

        LOGGER.info(f"Requesting subscription to { postbackUrl }")
        LOGGER.info(f"Pragma is set to { self.currentPragma }")

        body = {
            'subscription': {
                'postback_url': postbackUrl,
                'metadata': {
                    'headers': {
                        'Pragma': self.currentPragma
                    }
                }
             }
        }

        return self._callApi(method='PATCH', url='/subscription', body=body)

    def getCurrentPragma(self):
        return self.currentPragma

    def unsubscribe(self):
        return self._callApi(method='DELETE', url='/subscription')

    def getUserInfo(self):
        return self._callApi(url='/user/info')

    def floodlightOn(self, deviceId):
        return self._callApi(method='PUT', url=f"/devices/{ deviceId }/floodlight_on")

    def floodlightOff(self, deviceId):
        return self._callApi(method='PUT', url=f"/devices/{ deviceId }/floodlight_off")
