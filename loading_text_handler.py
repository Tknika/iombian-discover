#!/usr/bin/env python

import logging
import time

logger = logging.getLogger(__name__)

class LoadingTextHandler(object):

    def __init__(self, element, device_list, period=1, ticks=5):
        self.element = element
        self.device_list = device_list
        self.period = period
        self.last_scanning_update = time.time()
        self.ticks = 0

    def handle(self):
        if time.time() - self.last_scanning_update > self.period:
            if len(self.device_list) == 0:
                self.ticks = self.ticks + 1 if self.ticks < 5 else 0
                self.element.Update("Scanning devices" + self.ticks*" .")
            self.last_scanning_update = time.time()
