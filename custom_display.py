import gc
import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_shapes.filled_polygon import FilledPolygon


class CustomDisplay(displayio.Group):
    def __init__(self, display, *):
        super().__init__()
        self.display = display
        self.bitmap = displayio.Bitmap(32, 32, 16)
        self.color = displayio.Palette(10)
        self.color[0] = 0x000000  # black background
        self.color[1] = 0xFF0000  # red
        self.color[2] = 0xCC4000  # amber
        self.color[3] = 0x00FF00  # green
        self.color[4] = 0x00FFFF  # cyan
        self.color[5] = 0x666666  # lighter white
        self.color[6] = 0x006AFF  # cold
        self.color[7] = 0x00FF0F  # good
        self.color[8] = 0xFFAA00  # warm
        self.color[9] = 0xFF1000  # hot
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.color)
        self.root_group = displayio.Group()
        self.root_group.append(self)
        self.big_digits = displayio.Group()
        self.append(self.big_digits)
        self.hum_digits = displayio.Group()
        self.append(self.hum_digits)
        self.pm02_digits = displayio.Group()
        self.append(self.pm02_digits)
        self.lines = displayio.Group()
        self.append(self.lines)
        self.icons = displayio.Group()
        self.append(self.icons)
        self.display.root_group = self.root_group

        self.temperature = 888.8
        self.humidity = 888
        self.pm02 = 888
        self.make_lines()
        self.make_icons()
        self.update_display()

    def make_icons(self):
        # droplet
        self.icons.append(
            FilledPolygon(
                [
                    (28, 15),
                    (30, 17),
                    (30, 19),
                    (29, 20),
                    (27, 20),
                    (26, 19),
                    (26, 17),
                    (28, 15),
                ],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )
        )
        # %
        self.icons.append(
            FilledPolygon(
                [(18, 14), (19, 14), (19, 15), (18, 15), (18, 14)],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )
        )
        self.icons.append(
            FilledPolygon(
                [(21, 19), (22, 19), (22, 20), (21, 20), (21, 19)],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )
        )
        self.icons.append(Line(22, 14, 18, 20, self.color[4]))
        # pm02
        self.icons.append(Line(18, 25, 18, 28, self.color[2]))
        self.icons.append(Line(19, 25, 19, 26, self.color[2]))
        self.icons.append(Line(21, 25, 21, 28, self.color[2]))
        self.icons.append(Line(22, 25, 22, 26, self.color[2]))
        self.icons.append(Line(23, 25, 23, 28, self.color[2]))
        self.icons.append(Line(25, 27, 25, 30, self.color[2]))
        self.icons.append(Line(26, 27, 26, 30, self.color[2]))
        self.icons.append(Line(28, 27, 29, 27, self.color[2]))
        self.icons.append(Line(29, 28, 28, 29, self.color[2]))
        self.icons.append(Line(28, 30, 29, 30, self.color[2]))

    def make_lines(self):
        self.lines.append(Line(1, 12, 30, 12, self.color[5]))
        self.lines.append(Line(1, 22, 30, 22, self.color[5]))

    def make_big_digit(self, digit, position, color):
        offset = 0

        if position == 0:
            offset = 0
        elif position == 1:
            offset = 7
        elif position == 2:
            offset = 14
        elif position == 3:
            offset = 21
        elif position == 4:
            offset = 24
        else:
            offset = 0

        polygon = None
        if digit == "0":
            polygon = FilledPolygon(
                [
                    (1 + offset, 1),
                    (1 + offset, 9),
                    (5 + offset, 9),
                    (5 + offset, 1),
                    (1 + offset, 1),
                ],
                outline=color,
                stroke=2,
                fill=self.color[0],
            )
        elif digit == "1":
            polygon = Polygon(
                [
                    (5 + offset, 1),
                    (5 + offset, 10),
                    (6 + offset, 10),
                    (6 + offset, 1),
                    (5 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "2":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 6),
                    (2 + offset, 6),
                    (2 + offset, 9),
                    (6 + offset, 9),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 5),
                    (5 + offset, 5),
                    (5 + offset, 2),
                    (1 + offset, 2),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "3":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 6),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 9),
                    (5 + offset, 9),
                    (5 + offset, 6),
                    (1 + offset, 6),
                    (1 + offset, 5),
                    (5 + offset, 5),
                    (5 + offset, 2),
                    (1 + offset, 2),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "4":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (2 + offset, 1),
                    (2 + offset, 5),
                    (5 + offset, 5),
                    (5 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 10),
                    (5 + offset, 10),
                    (5 + offset, 6),
                    (1 + offset, 6),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "5":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 2),
                    (2 + offset, 2),
                    (2 + offset, 5),
                    (6 + offset, 5),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 9),
                    (5 + offset, 9),
                    (5 + offset, 6),
                    (1 + offset, 6),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "6":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 2),
                    (2 + offset, 2),
                    (2 + offset, 5),
                    (6 + offset, 5),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 9),
                    (5 + offset, 9),
                    (5 + offset, 6),
                    (2 + offset, 6),
                    (2 + offset, 9),
                    (1 + offset, 9),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "7":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 10),
                    (5 + offset, 10),
                    (5 + offset, 2),
                    (1 + offset, 2),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "8":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 6),
                    (2 + offset, 6),
                    (2 + offset, 9),
                    (5 + offset, 9),
                    (5 + offset, 2),
                    (2 + offset, 2),
                    (2 + offset, 5),
                    (4 + offset, 5),
                    (4 + offset, 6),
                    (1 + offset, 6),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == "9":
            polygon = Polygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 9),
                    (5 + offset, 9),
                    (5 + offset, 6),
                    (1 + offset, 6),
                    (1 + offset, 2),
                    (2 + offset, 2),
                    (2 + offset, 5),
                    (5 + offset, 5),
                    (5 + offset, 2),
                    (1 + offset, 2),
                    (1 + offset, 1),
                ],
                outline=color,
            )
        elif digit == ".":
            polygon = Polygon(
                [
                    (1 + offset, 9),
                    (1 + offset, 10),
                    (2 + offset, 10),
                    (2 + offset, 9),
                    (1 + offset, 9),
                ],
                outline=color,
            )
        elif digit == "-":
            polygon = Polygon(
                [
                    (1 + offset, 5),
                    (6 + offset, 5),
                    (6 + offset, 6),
                    (1 + offset, 6),
                    (1 + offset, 5),
                ],
                outline=color,
            )
        else:
            polygon = FilledPolygon(
                [
                    (1 + offset, 1),
                    (6 + offset, 1),
                    (6 + offset, 10),
                    (1 + offset, 10),
                    (1 + offset, 1),
                ],
                fill=self.color[0],
                outline=self.color[0],
                stroke=1,
            )

        if len(self.big_digits) >= 5:
            self.big_digits[position] = polygon
        else:
            self.big_digits.insert(position, polygon)

    def make_small_digit(self, digit, position, row, color):
        xoffset = 0
        yoffset = 0

        if position == 0:
            xoffset = 2
        elif position == 1:
            xoffset = 7
        elif position == 2:
            xoffset = 12
        else:
            xoffset = 0

        if row == 1:
            yoffset = 14
        else:
            yoffset = 24

        # polygon = None
        digit_group = displayio.Group()
        if digit == "0":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 6 + yoffset, 0 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 6 + yoffset, 0 + xoffset, 0 + yoffset, color)
            )
        elif digit == "1":
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
        elif digit == "2":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 3 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 3 + yoffset, 0 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 6 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
        elif digit == "3":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 6 + yoffset, 0 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 3 + yoffset, 3 + xoffset, 3 + yoffset, color)
            )
        elif digit == "4":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 3 + yoffset, 3 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
        elif digit == "5":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 3 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 3 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 6 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
        elif digit == "6":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 0 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 3 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 3 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 6 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
        elif digit == "7":
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
        elif digit == "8":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 6 + yoffset, 0 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 6 + yoffset, 0 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 3 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
        elif digit == "9":
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 3 + xoffset, 0 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 0 + yoffset, 3 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(3 + xoffset, 6 + yoffset, 0 + xoffset, 6 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 0 + yoffset, 0 + xoffset, 3 + yoffset, color)
            )
            digit_group.append(
                Line(0 + xoffset, 3 + yoffset, 3 + xoffset, 3 + yoffset, color)
            )
        else:
            digit_group.append(Line(0, 0, 0, 0, self.color[0]))

        if row == 1:
            if len(self.hum_digits) >= 3:
                self.hum_digits[position] = digit_group
            else:
                self.hum_digits.insert(position, digit_group)
        else:
            if len(self.pm02_digits) >= 3:
                self.pm02_digits[position] = digit_group
            else:
                self.pm02_digits.insert(position, digit_group)

    def make_droplet(self, humidity):
        if humidity < 20:
            self.icons[0] = FilledPolygon(
                [(28, 19), (29, 20), (27, 20), (28, 19)],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )
        elif humidity >= 20 and humidity < 40:
            self.icons[0] = FilledPolygon(
                [(27, 18), (29, 18), (30, 19), (29, 20), (27, 20), (26, 19), (27, 18)],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )
        elif humidity >= 40 and humidity < 60:
            self.icons[0] = FilledPolygon(
                [
                    (28, 16),
                    (30, 18),
                    (30, 19),
                    (29, 20),
                    (27, 20),
                    (26, 19),
                    (26, 18),
                    (28, 16),
                ],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )
        else:
            self.icons[0] = FilledPolygon(
                [
                    (28, 15),
                    (30, 17),
                    (30, 19),
                    (29, 20),
                    (27, 20),
                    (26, 19),
                    (26, 17),
                    (28, 15),
                ],
                stroke=1,
                outline=self.color[4],
                fill=self.color[4],
            )

    def update_display(self):
        temp_str = "{0:.1f}".format(self.temperature)
        if self.temperature < 0.0 and self.temperature > -10.0:
            temp_str = "+" + temp_str
        if self.temperature < 100.0 and self.temperature >= 0.0:
            temp_str = "+" + temp_str
        if self.temperature < 10.0 and self.temperature >= 0.0:
            temp_str = "+" + temp_str

        temp_color = self.color[0]
        if self.temperature < 65.0:
            temp_color = self.color[6]
        elif self.temperature >= 65.0 and self.temperature < 75.0:
            temp_color = self.color[7]
        elif self.temperature >= 75.0 and self.temperature < 85.0:
            temp_color = self.color[8]
        elif self.temperature >= 85.0:
            temp_color = self.color[9]

        for i, ch in enumerate(temp_str):
            self.make_big_digit(ch, i, temp_color)

        hum_str = str(round(self.humidity))
        if int(hum_str) < 100:
            hum_str = "+" + hum_str
        if int(hum_str) < 10:
            hum_str = "+" + hum_str

        for i, ch in enumerate(hum_str):
            self.make_small_digit(ch, i, 1, self.color[4])

        self.make_droplet(self.humidity)

        pm02_str = str(round(self.pm02))
        if int(pm02_str) < 100:
            pm02_str = "+" + pm02_str
        if int(pm02_str) < 10:
            pm02_str = "+" + pm02_str

        for i, ch in enumerate(pm02_str):
            self.make_small_digit(ch, i, 2, self.color[2])
        gc.collect()

    def set_environmentals(self, temperature, humidity, pm02):
        self.temperature = temperature
        self.humidity = humidity
        self.pm02 = pm02
    
    def set_temperature(self, temperature):
        self.temperature = temperature
    
    def set_humidity(self, humidity):
        self.humidity = int(humidity)
    
    def set_pm02(self, pm02):
        self.pm02 = int(pm02)
