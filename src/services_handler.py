#!/usr/bin/env python

import logging
import subprocess
import sys
import webbrowser

logger = logging.getLogger(__name__)

def launch_service(info):
    type = info["type"]
    if type == "web":
        return launch_service_web(info)
    elif type == "smb":
        return launch_service_smb(info)
    else:
        logger.warn("Unkwnon service: {}".format(type))
    return

def launch_service_web(info):
    ip = info["ip"]
    port = info["port"]
    url = "http://{}:{}".format(ip, port)
    logger.debug("Openning web url: '{}'".format(url))
    webbrowser.open_new_tab(url)
    return True

def launch_service_smb(info):
    ip = info["ip"]
    uri = "smb://{}".format(ip)
    if sys.platform == "linux":
        logger.debug("Openning smb folder: '{}'".format(uri))
        subprocess.Popen(["xdg-open", uri])
        return True
    elif sys.platform == "win32":
        uri = "//{}".format(ip)
        logger.debug("Openning smb folder: '{}'".format(uri))
        subprocess.Popen('explorer "{0}"'.format(uri))
        return True
    elif sys.platform == 'darwin':
        logger.debug("Openning smb folder: '{}'".format(uri))
        subprocess.Popen(["open", uri])
        return True
    else:
        logger.warn("Unknown system platform: {}".format(sys.platform))
    return