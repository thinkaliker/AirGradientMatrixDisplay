# AirGradientMatrixDisplay
Code for displaying Air Gradient sensor information on a CircuitPython LED RGB matrix

# Requires
- CircuitPython 9+
- 32x32 LED RGB Matrix
- Adafruit Metro M4 Airlift Lite (or equivalent)
- Adafruit RGB Matrix Shield (with CLK to A4 modification) (or equivalent)
- 5v power source
- AirGradient sensor
- Libraries (not all likely needed)
  - adafruit_bitmap_font
  - adafruit_bus_device
  - adafruit_connection_manager
  - adafruit_display_text
  - adafruit_display_shapes
  - adafruit_esp32spi
  - adafruit_fakerequests
  - adafruit_io
  - adafruit_matrixportal
  - adafruit_minimqtt
  - adafruit_miniqr
  - adafruit_pixelbuf
  - adafruit_portalbase
  - adafruit_requests
  - adafruit_ticks
  - neopixel
  - simpleio

# Configuration
- Modify settings.toml

# Display
- Temperature
  - Changes color based on how cold/hot it is
- Humidity (corrected)
  - Droplet changes size based on how humid it is
- PM02 (corrected)
  - for some reason the third topic doesn't work with MQTT

# Notes
- The Adafruit requests library has issues with lots of requests after some time. The try except is intened to try to fix that.
- I could not get the matrixportal Network library to work with my Metro M4. I ended up using the example code to establish a connection. This also means the onboard NeoPixel doesn't show network status.
- The display only shows F.
- MQTT is the new implementation because I couldn't query the endpoint directly anymore for some reason.
