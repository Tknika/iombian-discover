#!/usr/bin/env python

import collections
import logging
import time

logger = logging.getLogger(__name__)

class Device(object):
    def __init__(self, id="", hostname="", ip="", port="", properties="", state="", last_message=""):
        self.id = id
        self.hostname = hostname
        self.ip = ip if not isinstance(ip, list) else ip[0]
        self.port = port
        self.properties = properties
        self.state = state
        self.last_message = last_message or time.time()

    def update_device(self, hostname="", ip="", port="", properties="", state="", last_message=""):
        self.hostname = hostname if hostname else self.hostname
        if ip: self.ip = ip if not isinstance(ip, list) else ip[0]
        self.port = port if port else self.port
        self.properties = properties if properties else self.properties
        self.state = state if state else self.state
        self.last_message = last_message if last_message else time.time()

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
        return [self.hostname, self.ip, self.state, time.strftime("%Y/%m/%d %H:%M", time.localtime(self.last_message))]

    def __str__(self):
        return 'id: {}\n \
                hostname: {}\n \
                ip: {}\n \
                port: {}\n \
                properties: {}\n \
                state: {}'.format(self.id, self.hostname, self.ip, self.port, self.properties, self.state)


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

    def update_device(self, id="", hostname="", ip="", port="", properties="", state="", last_message=""):
        if id in self.devices:
            logger.debug("Device '{}' is in devices, should be updated".format(id))
            device = self.devices[id]
            device.update_device(id, hostname, ip, port, properties, state, last_message)
        else:
            logger.debug("Device '{}' is not in devices, should be created".format(id))
            self.devices[id] = Device(id, hostname, ip, port, properties, state, last_message)
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