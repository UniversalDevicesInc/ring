#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import json
import time
import re
import requests
from udi_interface import LOGGER, Custom, OAuth
# from requests.exceptions import HTTPError

# Implements the API calls to Ring
# It inherits the OAuth class
class RingInterface(OAuth):
    ringApiBasePath = 'https://api.ring.com/integrations/v1'

    def __init__(self, polyglot):
        super().__init__(polyglot)

        self.poly = polyglot
        self.customParams = Custom(polyglot, 'customparams')
        self.includeShared = False
        LOGGER.info('Ring interface initialized...')

    def customDataHandler(self, data):
        if data is not None and data.get('token'):
            LOGGER.info('Migrating tokens for new Ring version')
            # Save token data to the new oAuthTokens custom
            Custom(self.poly, 'oauthTokens').load(data['token'], True)

            # Save customdata without the key 'token'
            newData = { key: value for key, value in data.items() if key != 'token'}
            Custom(self.poly, 'customdata').load(newData, True)

            # Continue processing as if it was in the right place
            self.customNsHandler('oauthTokens', data['token'])

    def customNsHandler(self, key, data):
        LOGGER.debug('customNsHandler {}: {}'.format(key, json.dumps(data)))
        super().customNsHandler(key, data)

    def oauthHandler(self, token):
        LOGGER.debug('oAuth handler: {}'.format(json.dumps(token)))
        super().oauthHandler(token)

    def customParamsHandler(self, customParams):
        self.customParams.load(customParams)
        self.includeShared = ('shared' in self.customParams and self.customParams['shared'].lower() == 'true')
        LOGGER.info(f"Include shared devices: { self.includeShared }")
        LOGGER.debug(f"CustomParams: { json.dumps(customParams) }")

        if customParams is not None:
            oauthSettingsUpdate = {}

            if 'client_id' in customParams:
                oauthSettingsUpdate['client_id'] = customParams['client_id']
                LOGGER.info(f"oAuth client_id set to: { customParams['client_id'] }")

            if 'client_secret' in customParams:
                oauthSettingsUpdate['client_secret'] = customParams['client_secret']
                LOGGER.info('oAuth secret set to: ********')

            if 'my_auth_param' in customParams:
                if 'parameters' not in oauthSettingsUpdate:
                    oauthSettingsUpdate['parameters'] = {}

                oauthSettingsUpdate['parameters']['my_auth_param'] = customParams['my_auth_param']
                LOGGER.info(f"Setting oAuth my_auth_param to: { customParams['my_auth_param'] }")

            if 'my_token_param' in customParams:
                if 'token_parameters' not in oauthSettingsUpdate:
                    oauthSettingsUpdate['token_parameters'] = {}

                oauthSettingsUpdate['token_parameters']['my_token_param'] = customParams['my_token_param']
                LOGGER.info(f"Setting oAuth my_token_param to: { customParams['my_token_param'] }")

            LOGGER.debug(f"Updating oAuth config using: { json.dumps(oauthSettingsUpdate) }")

            self.updateOauthSettings(oauthSettingsUpdate)

            LOGGER.info(f"Updated oAuth config: { self.getOauthSettings() }")

    # Convert nodeserver address to a ring device id (Strip non-numeric characters)
    def addressToId(self, address):
        return int(re.sub(r"[^\d]+", '', address))

    def getPostbackUrl(self, uuid, slot):
        config = self.poly.getConfig()

        if config['store'].lower() == 'local':
            host = 'dev.isy.io'
        else:
            host = 'my.isy.io'

        LOGGER.info(f"Store is {config['store']}: Using hostname { host } for webhook url")

        return f"https://{ host }/api/eisy/pg3/webhook/noresponse/{ uuid }/{ slot }"

    # Call a Ring API
    def _callApi(self, method='GET', url=None, body=None):
        if url is None:
            LOGGER.error('url is required')
            return None

        completeUrl = self.ringApiBasePath + url

        LOGGER.info(f"Making call to { method } { completeUrl }")

        # Then calling an API, get the access token (it will be refreshed if necessary)
        accessToken = self.getAccessToken()

        # if accessToken is None:
        #     LOGGER.debug('Access token is not available')
        #     return None

        headers = {
            'Authorization': f"Bearer { accessToken }"
        }

        if method in [ 'PATCH', 'POST'] and body is None:
            LOGGER.error(f"body is required when using { method } with { completeUrl }")

        try:
            # Simulate 401 before making actual requests
            # mock_response = requests.Response()
            # mock_response.status_code = 401
            # mock_response._content = b'{"message": "Unauthorized access"}'
            # mock_response.url = completeUrl
            # mock_response.reason = 'Unauthorized'
            # http_error = HTTPError(response=mock_response)
            # http_error.response = mock_response
            # raise http_error

            # Simulate DNS failure
            # raise requests.exceptions.ConnectionError("DNS lookup failed")

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
            LOGGER.info(f"Call { method } { completeUrl } successful")
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text

        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 401:
                LOGGER.error(f"Call {method} {completeUrl} failed with status code 401. Asking to re-authorize.")
                self.poly.Notices['auth'] = 'Please initiate authentication'

            else:
                LOGGER.error(
                    f"Call {method} {completeUrl} failed with status {error.response.status_code}: "
                    f"{error.response.text}"
                )
            raise

        except requests.exceptions.ConnectionError as error:
            LOGGER.error(f"Connection error occurred: {error}")
            raise
        except requests.exceptions.Timeout as error:
            LOGGER.error(f"Timeout error occurred: {error}")
            raise
        except requests.exceptions.RequestException as error:
            LOGGER.error(f"Request error occurred: {error}")
            raise
        except Exception:
            # Catch any other unexpected exceptions as a last resort
            LOGGER.exception("Unexpected error occurred during Ring API call")
            raise



    # Call a Ring API to test connectivity
    def testApiCall(self):
        return self._callApi(url='/user/info')

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
                LOGGER.error(f"MQTT connection not online.\nOn my.isy.io, please check Select Tool | PG3 | Remote connection. It has to be active.\nIf you don't see the option, your device does not support it. Make sure you are using an eisy at 5.6.0 or more recent, or a Polisy using PG3x.")
            # No access to uuid?
            elif httpStatus == 423:
                LOGGER.error(f"Make sure that uuid { config['uuid'] } is in your portal account, has a license and is authorized.")
            else:
                LOGGER.error(f"Call event url failed GET { completeUrl } failed with HTTP { httpStatus }: { error }")

            raise Exception('Error sending event to Portal webhook')

    def getAllDevices(self):
        try:
            return self._callApi(url='/devices')
        except Exception:
            return None

    def getDeviceData(self, id, prefetched=None):
        if prefetched is None:
            LOGGER.info('prefetched is none')
            devices = self.getAllDevices()
        else:
            devices = prefetched

        # If we don't have authorizations, devices will be null
        if devices is None:
            return

        allDevices = devices['doorbells'] + devices['authorized_doorbells'] + devices['stickup_cams']
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

        try:
            return self._callApi(method='PATCH', url='/subscription', body=body)
        except Exception:
            return None

    def getCurrentPragma(self):
        return getattr(self, 'currentPragma', None)

    def unsubscribe(self):
        try:
            return self._callApi(method='DELETE', url='/subscription')
        except Exception:
            return None

    def getUserInfo(self):
        try:
            return self._callApi(url='/user/info')
        except Exception:
            return None

    def floodlightOn(self, deviceId):
        try:
            return self._callApi(method='PUT', url=f"/devices/{ deviceId }/floodlight_on")
        except Exception:
            return None

    def floodlightOff(self, deviceId):
        try:
            return self._callApi(method='PUT', url=f"/devices/{ deviceId }/floodlight_off")
        except Exception:
            return None
