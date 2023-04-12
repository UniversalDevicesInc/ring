#!/usr/bin/env python3
"""
Polyglot v3 controller node
Copyright (C) 2023 Universal Devices

MIT License
"""
import requests
from udi_interface import LOGGER, Node
from nodes.doorbell import Doorbell
from nodes.doorbellMotion import DoorbellMotion
from nodes.camera import Camera
from nodes.cameraLight import CameraLight

# siren is currently not used
DEVICE_TYPES = {
  'base_station_v1': { 'name': 'Ring Alarm Base Station', 'lights': False },
  'beams_bridge_v1': { 'name': 'Ring Bridge Hub', 'lights': False },
  'chime_pro_v2': { 'name': 'Ring Chime Pro (v2)', 'lights': False },
  'chime_pro': { 'name': 'Ring Chime Pro', 'lights': False },
  'chime': { 'name': 'Ring Chime', 'lights': False },
  'cocoa_camera': { 'name': 'Ring Stick Up Cam', 'lights': False, 'siren': True },
  'cocoa_doorbell': { 'name': 'Ring Video Doorbell 2020', 'lights': False },
  'cocoa_floodlight': { 'name': 'Ring Floodlight Cam Wired Plus', 'lights': True, 'siren': True },
  'doorbell_portal': { 'name': 'Ring Peephole Cam', 'lights': False },
  'doorbell_scallop_lite': { 'name': 'Ring Video Doorbell 3', 'lights': False },
  'doorbell_scallop': { 'name': 'Ring Video Doorbell 3 Plus', 'lights': False },
  'doorbell_v3': { 'name': 'Ring Video Doorbell', 'lights': False },
  'doorbell_v4': { 'name': 'Ring Video Doorbell 2', 'lights': False },
  'doorbell_v5': { 'name': 'Ring Video Doorbell 2', 'lights': False },
  'doorbell': { 'name': 'Ring Video Doorbell', 'lights': False },
  'floodlight_v2': { 'name': 'Ring Floodlight Cam Wired', 'lights': True, 'siren': True },
  'hp_cam_v1': { 'name': 'Ring Floodlight Cam', 'lights': True, 'siren': True },
  'hp_cam_v2': { 'name': 'Ring Spotlight Cam Wired', 'lights': True, 'siren': True },
  'jbox_v1': { 'name': 'Ring Video Doorbell Elite', 'lights': False },
  'lpd_v1': { 'name': 'Ring Video Doorbell Pro', 'lights': False },
  'lpd_v2': { 'name': 'Ring Video Doorbell Pro 2', 'lights': False },
  'lpd_v4': { 'name': 'Ring Video Doorbell Pro 2', 'lights': False },
  'spotlightw_v2': { 'name': 'Ring Spotlight Cam Wired', 'lights': True, 'siren': True },
  'stickup_cam_elite': { 'name': 'Ring Stick Up Cam Wired', 'lights': False },
  'stickup_cam_lunar': { 'name': 'Ring Stick Up Cam Battery', 'lights': False },
  'stickup_cam_mini': { 'name': 'Ring Indoor Cam', 'lights': False },
  'stickup_cam_v3': { 'name': 'Ring Stick Up Cam', 'lights': False },
  'stickup_cam_v4': { 'name': 'Ring Spotlight Cam Battery', 'lights': True },
  'stickup_cam': { 'name': 'Ring Original Stick Up Cam', 'lights': False },
  'floodlight_pro': { 'name': 'Ring Floodlight pro', 'lights': True, 'siren': True }
}

class Controller(Node):
    # nodedef id
    id = 'CTL'

    drivers = [
        { 'driver': 'ST', 'value': 0, 'uom': 2 }
    ]

    def __init__(self, polyglot, parent, address, name, ringInterface):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.ring = ringInterface

        polyglot.addNode(self, conn_status='ST')

        LOGGER.info('Controller Initialized...')

    def discoverDevices(self, param=None):
        userInfo = self.ring.getUserInfo()
        self.userId = userInfo['user']['id']

        LOGGER.info(f"User id is: { self.userId }")

        self.devices = self.ring.getAllDevices()
        LOGGER.info(f'Devices: { self.devices }')

        for doorbellData in self.devices['doorbells']:
            ownerId = doorbellData['owner']['id']

            if ownerId == self.userId:
                addressDoorbell = str(doorbellData['id']) + '_db'  # Has to be _db to receive ding events
                nameDoorbell = doorbellData['description']
                doorbell = Doorbell(self.poly, self.address, addressDoorbell, nameDoorbell, self.ring)
                LOGGER.warn(f"Adding doorbell { addressDoorbell }: { nameDoorbell }")
                self.poly.addNode(doorbell)

                addressDoorbellMotion = str(doorbellData['id']) + '_m'   # Has to be _m to receive motion events
                nameDoorbellMotion = doorbellData['description'] + ' (Motion)'
                doorbellMotion = DoorbellMotion(self.poly, self.address, addressDoorbellMotion, nameDoorbellMotion, self.ring)
                LOGGER.warn(f"Adding doorbell motion node { addressDoorbellMotion }: { nameDoorbellMotion }")
                self.poly.addNode(doorbellMotion)
            else:
                LOGGER.warn(f"Adding doorbell { doorbellData['id'] } ({ doorbellData['description'] }) ignored: Doorbell is shared")

        for camData in self.devices['stickup_cams']:
            ownerId = doorbellData['owner']['id']

            if ownerId == self.userId:
                addressCamera = str(camData['id']) + '_m'  # Has to be _m to receive motion events
                nameCamera = camData['description'] + ' (Motion)'
                camera = Camera(self.poly, self.address, addressCamera, nameCamera, self.ring)
                LOGGER.warn(f"Adding camera { addressCamera }: { nameCamera }")
                self.poly.addNode(camera)

                kind = camData['kind']
                typeData = DEVICE_TYPES.get(kind, None)

                if typeData is None:
                    LOGGER.error(f"Device kind { kind } is not defined.\nDevice info: { camData }\n*** Please contact UDI support and copy/paste this log. ***")
                    continue

                if typeData.get('lights', False) is True:
                    addressCameraLight = str(camData['id']) + '_lt'
                    nameCameraLight = camData['description'] + ' (Lights)'
                    cameraLight = CameraLight(self.poly, self.address, addressCameraLight, nameCameraLight, self.ring)
                    LOGGER.warn(f"Adding camera lighting node { addressCameraLight }: { nameCameraLight }")
                    self.poly.addNode(cameraLight)
            else:
                LOGGER.warn(f"Adding camera { doorbellData['id'] } ({ doorbellData['description'] }) ignored: Camera is shared")


    # When node is added, automatically "query" using prefetched devices data from discoverDevices
    def addNodeDoneHandler(self, nodeData):
        address = nodeData['address']

        for node in self.poly.nodes():
            if node.address == address and hasattr(node, 'queryWithPrefetched'):
                node.queryWithPrefetched(self.devices)

    def queryAll(self, param=None):
        # Prefetch devices data
        self.devices = self.ring.getAllDevices()
        LOGGER.debug(f'Devices: { self.devices }')

        for node in self.poly.nodes():
            if hasattr(node, 'queryWithPrefetched'):
                # Run a query on all devices with prefetched data
                node.queryWithPrefetched(self.devices)

    # The commands here need to match what is in the nodedef profile file.
    commands = {
        'DISCOVER': discoverDevices,
        'QUERYALL': queryAll
        }


