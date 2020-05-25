#!/usr/bin/env python

import logging
from zeroconf import ServiceBrowser, Zeroconf

logger = logging.getLogger(__name__)


class DiscoveryHandler(object):

    def __init__(self, service_name, devices_handler):
        self.service_name = service_name
        self.devices_handler = devices_handler
        self.zeroconf = Zeroconf()
        self.listener = DeviceDiscoverListener(self.devices_handler)

    def start(self):
        self.browser = ServiceBrowser(self.zeroconf, self.service_name, self.listener)

    def stop(self):
        self.zeroconf.close()


class DeviceDiscoverListener(object):

    def __init__(self, devices_handler):
        self.devices_handler = devices_handler

    def remove_service(self, zeroconf, type, name):
        logger.info("Service '{}' removed".format(name))
        id = name
        self.devices_handler.update_device(id, available=False)

    def add_service(self, zeroconf, type, name):
        logger.info("Service {} added".format(name))
        info = zeroconf.get_service_info(type, name)
        logger.debug("Service info:\n{}".format(info))
        try:
            id = name
            hostname = info.server[:-1]
            ip = info.parsed_addresses()
            port = info.port
            properties = info.properties
            self.devices_handler.update_device(id, hostname, ip, port, properties, True)
        except AttributeError:
            logger.error("Service info for '{}' could not be loaded".format(name))
            self.devices_handler.update_device(name)