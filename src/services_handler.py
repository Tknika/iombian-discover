#!/usr/bin/env python

from enum import Enum
import logging
import os
import subprocess
import sys
import webbrowser

logger = logging.getLogger(__name__)

class OS(Enum):
    Linux = "linux"
    Windows = "win32"
    MacOS = "darwin"

def launch_service(info):
    type = info["type"]
    if type == "web":
        return launch_service_web(info)
    elif type == "smb":
        return launch_service_smb(info)
    elif type == "ssh":
        return launch_service_ssh(info)
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
    if sys.platform == OS.Linux.value:
        logger.debug("Openning smb folder: '{}'".format(uri))
        if __check_command("nautilus"):
            subprocess.Popen(["nautilus", uri])
        else:
            subprocess.Popen(["xdg-open", uri])
    elif sys.platform == OS.Windows.value:
        uri = "\\\\{}".format(ip)
        logger.debug("Openning smb folder: '{}'".format(uri))
        subprocess.Popen('explorer "{0}"'.format(uri))
    elif sys.platform == OS.MacOS.value:
        logger.debug("Openning smb folder: '{}'".format(uri))
        subprocess.Popen(["open", uri])
    else:
        logger.warn("Unknown system platform: {}".format(sys.platform))
        return False
    return True

def launch_service_ssh(info):
    ip = info["ip"]
    port = info["port"]
    user = info["user"]
    if sys.platform == OS.Linux.value:
        # Check gnome-terminal
        if __check_command("gnome-terminal"):
            command = "ssh -p {} {}@{}".format(port, user, ip)
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', command])
        else:
            # TO-DO: Add more terminal applications (Konsole...)
            return False
    elif sys.platform == OS.Windows.value:
        putty_path_64 = r"C:\Program Files\PuTTy\putty.exe"
        putty_path_32 = r"C:\Program Files (x86)\PuTTy\putty.exe"
        putty_path = __check_paths([putty_path_64, putty_path_32])
        if putty_path:
            subprocess.Popen("{} {}@{} -P {}".format(putty_path, user, ip, port))
        else:
            logger.warn("PuTTy is not installed, service not available")
            return False
    elif sys.platform == OS.MacOS.value:
        # TO-DO: Implement it on MacOS
        return False
    else:
        logger.warn("Unknown system platform: {}".format(sys.platform))
        return False
    return True

def __check_command(name):
    return not subprocess.call(["which", name])

def __check_paths(paths):
    if isinstance(paths, str):
        return paths if os.path.exists(paths) else None
    elif isinstance(paths, list):
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    else:
        logger.warn("Paths type '{}' can not be processed".format(type(paths)))