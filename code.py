# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Matrix Weather display
# For Metro M4 Airlift with RGB Matrix shield, 64 x 32 RGB LED Matrix display

"""
This example queries the Open Weather Maps site API to find out the current
weather for your location... and display it on a screen!
if you can find something that spits out JSON data, we can display it
"""
from os import getenv
import gc
import time
import json
import board
import busio
import displayio
import terminalio
import microcontroller
from digitalio import DigitalInOut, Direction, Pull
import adafruit_connection_manager
import adafruit_requests
from adafruit_display_text import label
#from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_esp32spi import adafruit_esp32spi

import custom_display

secrets = {
    "ssid": getenv("CIRCUITPY_WIFI_SSID"),
    "password": getenv("CIRCUITPY_WIFI_PASSWORD"),
}
gc.enable()
matrix = Matrix(width=32, height=32)

display = matrix.display
#display.root_group = None
#displayio.release_displays()
group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(32, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x00FF00  # greenish
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.root_group = group
#font = terminalio.FONT
display_text = 'init'
screen_text = label.Label(terminalio.FONT, text=display_text)
screen_text.x = 5
screen_text.y = 15
screen_text.color = 0x00FF00
group.append(screen_text)

if secrets == {"ssid": None, "password": None}:
    try:
        # Fallback on secrets.py until depreciation is over and option is removed
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in settings.toml, please add them there!")
        raise

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# Secondary (SCK1) SPI used to connect to WiFi board on Arduino Nano Connect RP2040
if "SCK1" in dir(board):
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
else:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

screen_text.text = 'WiFi'
print("Connecting to " + secrets["ssid"] + "...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", esp.ap_info.ssid, "\tRSSI:", esp.ap_info.rssi)
print("IP address is", esp.ipv4_address)

DATA_SOURCE = (
    #"http://api.openweathermap.org/data/2.5/weather?q=" + LOCATION + "&units=" + UNITS
    "http://" + getenv("AIRGRADIENT_IP") + "/measures/current"
)
print("Fetching text from", DATA_SOURCE)

main_display = custom_display.CustomDisplay(matrix.display)

reset_counter = 0

while True:
    try:
        req = requests.get(DATA_SOURCE, timeout=120, headers={'Connection': 'close'})
        recv_data = req.json()
        current_atmp = float(recv_data['atmpCompensated']) * (9 / 5) + 32
        current_hum = float(recv_data['rhumCompensated'])
        current_pm02 = float(recv_data['pm02Compensated'])
        print('atmp ' + str(current_atmp) + '\t' + 'hum ' + str(current_hum) + '\tpm02 ' + str(current_pm02))
        #screen_text.text = str(current_atmp) + '\n' + str(current_hum)
        main_display.set_environmentals(current_atmp, current_hum, current_pm02)
        main_display.update_display()
        gc.collect()
        req.close()
    except Exception as e:
        reset_counter += 1

    if reset_counter > 10:
        microcontroller.reset()
    time.sleep(60)
