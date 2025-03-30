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
import adafruit_minimqtt.adafruit_minimqtt as MQTT

import custom_display

secrets = {
    "ssid": getenv("CIRCUITPY_WIFI_SSID"),
    "password": getenv("CIRCUITPY_WIFI_PASSWORD"),
    "mqtt_host": getenv("MQTT_BROKER"),
    "mqtt_user": getenv("MQTT_USER"),
    "mqtt_pass": getenv("MQTT_PASS")
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

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["mqtt_host"],
    username=secrets["mqtt_user"],
    password=secrets["mqtt_pass"],
    socket_pool=pool,
    ssl_context=ssl_context,
)

mqtt_topic_temp = f"homeassistant/sensor/ag_outdoors_temperature/state"
mqtt_topic_hum = f"homeassistant/sensor/ag_outdoors_humidity/state"
mqtt_topic_pm25 = f"homeassistant/sensor/ag_outdoors_pm2_5/state"

current_atmp = 0.0
current_hum = 0.0
current_pm02 = 0.0

main_display = custom_display.CustomDisplay(matrix.display)

# Define callback methods which are called when events occur
def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print(f"Flags: {flags}\n RC: {rc}")

def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")

def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print(f"Subscribed to {topic} with QOS level {granted_qos}")

def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print(f"Unsubscribed from {topic} with PID {pid}")

def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print(f"Published to {topic} with PID {pid}")

def message(client, topic, message):
    print(f"New message on topic {topic}: {message}")
    if topic == mqtt_topic_temp:
        current_atmp = float(message)
        main_display.set_temperature(current_atmp)
    if topic == mqtt_topic_hum:
        current_hum = float(message)
        main_display.set_humidity(current_hum)
    if topic == mqtt_topic_pm25:
        current_pm02 = float(message)
        main_display.set_pm02(current_pm02)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message

print(f"Attempting to connect to {mqtt_client.broker}")
mqtt_client.connect()

print(f"Subscribing to {mqtt_topic_temp}")
mqtt_client.subscribe(mqtt_topic_temp)

print(f"Subscribing to {mqtt_topic_hum}")
mqtt_client.subscribe(mqtt_topic_hum)

print(f"Subscribing to {mqtt_topic_pm25}")
mqtt_client.subscribe(mqtt_topic_pm25)

reset_counter = 0

while True:
    try:
        main_display.update_display()
        gc.collect()
    except Exception as e:
        print("err: ", str(e))
        reset_counter += 1
    if reset_counter > 10:
        microcontroller.reset()
    time.sleep(60)
