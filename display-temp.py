from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time

import ST7789
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280

# initialise BME280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)


# Set up in "forced" mode
# In this mode `get_temperature` and `get_pressure` will trigger
# a new reading and wait for the result.
# The chip will return to sleep mode when finished.
bme280.setup(mode="normal", temperature_oversampling=1, pressure_oversampling=1)

tempA = bme280.get_temperature()
MESSAGE = '{:05.2f}*C'.format(tempA)


# Create ST7789 LCD display class.
disp = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)

# Initialize display.
disp.begin()

WIDTH = disp.width
HEIGHT = disp.height


img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))

draw = ImageDraw.Draw(img)

font = ImageFont.truetype(
    "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 60)

size_x, size_y = draw.textsize(MESSAGE, font)

text_x = disp.width
text_y = (80 - size_y) // 2

t_start = time.time()

while True:
    tempA = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    MESSAGE = '{:04.1f}°c'.format(tempA)

    draw.rectangle((0, 0, disp.width, 240), (0, 0, 0))
    draw.text((0, text_y), MESSAGE, font=font, fill=(255, 255, 255))
    MSG2 = '{:04.1f}'.format(humidity)
    draw.text((0, 120), MSG2, font=font, fill=(255,255,255))
    disp.display(img)
