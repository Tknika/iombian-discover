#!/usr/bin/env python

import collections
import logging
import time

logger = logging.getLogger(__name__)

class Device(object):
    def __init__(self, id="", hostname="", ip="", port="", properties="", available="", last_message=""):
        self.id = id
        self.hostname = hostname
        self.ip = ip if not isinstance(ip, list) else ip[0]
        self.port = port
        self.properties = properties
        self.available = available
        self.last_message = last_message or time.time()

    def update_device(self, hostname=None, ip=None, port=None, properties=None, available=None, last_message=None):
        self.hostname = hostname if hostname is not None else self.hostname
        if ip is not None: self.ip = ip if not isinstance(ip, list) else ip[0]
        self.port = port if port is not None else self.port
        self.properties = properties if properties is not None else self.properties
        self.available = available if available is not None else self.available
        self.last_message = last_message if last_message is not None else time.time()

    def is_available(self):
        return self.available

    def get_services(self):
        services = {}
        for name_bytes, port_bytes in self.properties.items():
            if name_bytes == b'org.freedesktop.Avahi.cookie':
                continue
            name = name_bytes.decode("utf-8")
            port = port_bytes.decode("utf-8")
            services[name] = "http://{}:{}".format(self.ip, port)
        return services

    def to_array(self):
        return [self.hostname, self.ip, self.available, time.strftime("%Y/%m/%d %H:%M", time.localtime(self.last_message))]

    def __str__(self):
        return 'id: {}\n \
                hostname: {}\n \
                ip: {}\n \
                port: {}\n \
                properties: {}\n \
                available: {}'.format(self.id, self.hostname, self.ip, self.port, self.properties, self.available)


class DevicesHandler(object):
    def __init__(self):
        self.devices = collections.OrderedDict()
        self.last_update = None

    def get_device(self, id):
        if not id in self.devices:
            logger.error("Device '{}' is not in devices".format(id))
            return
        return self.devices[id]

    def get_device_by_pos(self, pos):
        if pos >= len(self.devices):
            logger.error("Required position is bigger than the number of devices")
            return
        return list(self.devices.values())[pos]

    def update_device(self, id=None, hostname=None, ip=None, port=None, properties=None, available=None, last_message=None):
        if id in self.devices:
            logger.debug("Device '{}' is in devices, should be updated".format(id))
            device = self.devices[id]
            device.update_device(hostname, ip, port, properties, available, last_message)
        else:
            logger.debug("Device '{}' is not in devices, should be created".format(id))
            self.devices[id] = Device(id, hostname, ip, port, properties, available, last_message)
        self.last_update = time.time()

    def remove_device(self, id):
        if not id in self.devices:
            logger.error("Device '{}' is not in devices, cannot be deleted".format(id))
            return
        del self.devices[id]
        self.last_update = time.time()

    def to_array(self, hostname_filter=''):
        if not self.devices:
            return[["", "", "", ""]]
        if not hostname_filter:
            return [device.to_array() for device in self.devices.values()]
        else:
            return [device.to_array() for device in self.devices.values() if hostname_filter in device.hostname]

    def __len__(self):
        return len(self.devices)