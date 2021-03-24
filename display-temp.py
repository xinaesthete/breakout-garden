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
bme280.setup(mode="normal", temperature_oversampling=16, pressure_oversampling=16)

# hardcoded to ambient temperature according to thermostat at time of writing
initTemp = 18.5

tempA = bme280.get_temperature()
# for some reason first temp always seems to be 22.27269?
print('First measurement: {:04.5f}'.format(tempA))
time.sleep(0.1)
tempA = bme280.get_temperature()
tempOffset = tempA - initTemp
print('Second measurement: {:04.5f}, tempOffset: {:04.2f}'.format(tempA, tempOffset))
MESSAGE = '{:04.2f}*C'.format(tempA)


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

smallFont = ImageFont.truetype(
    "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 20)

midFont = ImageFont.truetype(
    "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 40)

size_x, size_y = draw.textsize(MESSAGE, font)

text_x = disp.width
text_y = (80 - size_y) // 2

t_start = time.time()


pressure = bme280.get_pressure()
pressureHistory = []
for i in range(240):
    pressureHistory.append(bme280.get_pressure())

while True:
    tempA = bme280.get_temperature() - tempOffset
    humidity = bme280.get_humidity()
    MESSAGE = '{:04.1f}°c'.format(tempA)

    draw.rectangle((0, 0, disp.width, disp.height), (0, 0, 0))
    draw.text((0, text_y), MESSAGE, font=font, fill=(255, 255, 255))
    MSG2 = '{:04.1f}'.format(humidity)
    draw.text((0, 90), 'humidity:', font=smallFont, fill=(255,255,255))
    draw.text((0, 110), MSG2, font=midFont, fill=(255,255,255))
    draw.text((0, 170), 'pressure:', font=smallFont, fill=(255,255,255))
    pressure = bme280.get_pressure()
    MSG3 = '{:04.4f}'.format(pressure)
    pressureHistory.append(pressure)
    pressureHistory.pop(0)
    draw.text((0, 190), MSG3, font=midFont, fill=(255, 255, 255))
    minP = min(pressureHistory)
    maxP = max(pressureHistory)
    x = 0
    y0 = 200 + 40 * (pressureHistory[0] - minP) / (maxP - minP)
    for val in pressureHistory:
        y = 200 + 40 * (val - minP) / (maxP - minP)
        draw.line([(x-1, y0), (x, y)], (80, 230, 230))
        x = x+1
        y0 = y

    disp.display(img)
    # time.sleep(0.05)
