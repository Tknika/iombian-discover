#!/usr/bin/env python

import json
import logging
import PySimpleGUI as sg
from devices_handler import DevicesHandler
from discovery_handler import DiscoveryHandler
from loading_text_handler import LoadingTextHandler
from services_handler import launch_service

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-20s  - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

SERVICE_NAME = "_iombian._tcp.local."

def create_services_layout(device):
    services = device.get_services()
    frame_layout = [[]]
    for name, info in services.items():
        key = json.dumps(info)
        hyperlink_element = sg.Button(name, enable_events=True, key=key)
        frame_layout.append([hyperlink_element])
    
    frame_element = sg.Frame("Services", frame_layout, key='services')
    layout = [[frame_element]]
    return layout

if __name__ == "__main__":
    logger.info("Starting 'iombian-discover'...")

    devices_handler = DevicesHandler()
    discovery = DiscoveryHandler(SERVICE_NAME, devices_handler)
    discovery.start()

    sg.theme('SystemDefault')

    headings=["Name", "IP", "Available", "Last Update"]
    data = [["" for i in range(len(headings))]]

    main_layout = [[sg.Input(focus=True, size=(60,1), enable_events=True, key='filter'), sg.Button('Reset Filter', key='reset')],
        [sg.Table(values=data, headings=headings, enable_events=True,  col_widths=[16,12,8,12],
                num_rows=10, justification='center', auto_size_columns=False, key='devices')],
        [sg.Text('Scanning devices', size=(40,1), key='selected_device')]]

    main_window = sg.Window('IoMBian discover', main_layout)
    services_window = None
    services_window_active = False

    loading_text = LoadingTextHandler(main_window["selected_device"], devices_handler)
    
    last_update = 0
    while True:
        event, values = main_window.read(50)

        if event in (None, "Exit"):
            break
        elif event == 'filter':
            filter_word = values.get('filter', '')
            main_window['devices'].update(values=devices_handler.to_array(hostname_filter=filter_word))
        elif event == 'reset':
            main_window["filter"].Update("")
            main_window["filter"].set_focus()
            main_window['devices'].update(values=devices_handler.to_array())
        elif event == 'devices':
            device_position = values.get('devices')[0]
            device = devices_handler.get_device_by_pos(device_position)
            if not device:
                continue
            if not device.is_available():
                logger.debug("Device '{}' is not available, services cannot be shown".format(device.hostname))
                sg.PopupAutoClose("'{}' not available".format(device.hostname), auto_close_duration=4)
                continue
            main_window["selected_device"].Update("Selected device: {}".format(device.hostname))
            logger.debug("Creating 'service' window for '{}' device".format(device.hostname))
            services_layout = create_services_layout(device)
            services_window = sg.Window('Services', services_layout)
            services_window_active = True

        if services_window_active:
            service_event, vals2 = services_window.read(timeout=50)
            if service_event in (None, "Exit"):
                services_window_active = False
                services_window.close()
                last_update = 0
            elif "type" in service_event:
                info = json.loads(service_event)
                ok = launch_service(info)
                if not ok:
                    sg.PopupAutoClose("Service not available", auto_close_duration=4)
                services_window_active = False
                services_window.close()
                last_update = 0

        if devices_handler.last_update != last_update:
            logger.debug("Updating devices table...")
            filter_word = values.get('filter', '')
            main_window['devices'].update(values=devices_handler.to_array(hostname_filter=filter_word))
            if len(devices_handler) > 0:
                main_window["selected_device"].Update("Select any available device to see its services")
            last_update = devices_handler.last_update

        loading_text.handle()

    main_window.close()
    discovery.stop()