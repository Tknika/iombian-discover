#!/usr/bin/env python

import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-20s  - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.debug("Starting 'iombian-controller'...")