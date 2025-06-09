#!/home/jeremy/Downloads/venv/bin/python
from luma.core.interface.serial import spi, noop
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.render import canvas
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT, TINY_FONT

from datetime import datetime, timedelta

import time
import signal
import sys
import requests
import json
import threading

# Initialize the SPI interface
serial = spi(port=0, device=0, gpio=noop())  # Use port=0, device=0 for the first SPI device
serial2 = spi(port=0, device=1, gpio=noop())

# Create a MAX7219 device with dimensions 32x8 (32 pixels wide and 8 pixels high)
device = max7219(serial, width=32, height=8, block_orientation=-90)  # Rotate 90 degrees if necessary
device.contrast(1)  # Set contrast (brightness level from 0 to 15)

device2 = max7219(serial2, width=32, height=8, block_orientation=-90)
device2.contrast(1)

arr = [[[0, 1, 1, 0],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0]],
	   
	   [[0, 0, 1, 0],
	    [0, 1, 1, 0],
	    [0, 0, 1, 0],
	    [0, 0, 1, 0],
	    [0, 0, 1, 0],
	    [0, 0, 1, 0],
	    [0, 1, 1, 1]],
	    
	   [[0, 1, 1, 0],
		[1, 0, 0, 1],
	    [0, 0, 0, 1],
	    [0, 0, 1, 0],
	    [0, 1, 0, 0],
	    [1, 0, 0, 0],
	    [1, 1, 1, 1]],

	   [[0, 1, 1, 0],
	    [1, 0, 0, 1],
	    [0, 0, 0, 1],
	    [0, 1, 1, 0],
	    [0, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0]],

	   [[1, 0, 1, 0],
	    [1, 0, 1, 0],
	    [1, 0, 1, 0],
	    [1, 1, 1, 1],
	    [0, 0, 1, 0],
	    [0, 0, 1, 0],
	    [0, 0, 1, 0]],

	   [[1, 1, 1, 1],
	    [1, 0, 9, 0],
	    [1, 0, 0, 0],
	    [0, 1, 1, 0],
	    [0, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0]],
	
	   [[0, 1, 1, 0],
	    [1, 0, 0, 1],
	    [1, 0, 0, 0],
	    [1, 1, 1, 0],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0]],

	   [[1, 1, 1, 1],
	    [0, 0, 0, 1],
	    [0, 0, 1, 0],
	    [0, 0, 1, 0],
	    [0, 1, 0, 0],
	    [0, 1, 0, 0],
	    [0, 1, 0, 0]],
	   
	   [[0, 1, 1, 0],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0]],
       
       [[0, 1, 1, 0],
	    [1, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 1],
	    [0, 0, 0, 1],
	    [1, 0, 0, 1],
	    [0, 1, 1, 0]]]

clock_loop = False
info_loop = False

def signal_term_handler(signal, frame):
	global clock_loop
	global info_loop
	clock_loop = False
	info_loop = False
	
def hour(hour, draw):
	drawNum(0, 0, hour // 10, draw)
	drawNum(5, 0, hour % 10, draw)
	
def minute(minute, draw):
	drawNum(11, 0, minute // 10, draw)
	drawNum(16, 0, minute % 10, draw)

def second(second, draw):
	drawNum(22, 0, second // 10, draw)
	drawNum(27, 0, second % 10, draw)
	
def drawNum(x, y, num, draw):
	for j in range(len(arr[num])):
		for i in range(len(arr[num][j])):
			if arr[num][j][i] == 1:
				draw.point((x + i, y + j), fill="white")
	
def drawTime():
	global clock_loop
	clock_loop = True
	while clock_loop:
		with canvas(device) as draw:
			dt = datetime.now()
			hour(int(dt.strftime("%H")), draw)
			draw.point((9, 7), fill="white")
			minute(int(dt.strftime("%M")), draw)
			draw.point((20, 7), fill="white")
			second(int(dt.strftime("%S")) , draw)
			time.sleep(1/30)
	device.cleanup()
	print("CLOCK END")
			

ip_data = requests.get("https://api.ipify.org").text
geo_data = requests.get("http://ip-api.com/json/"+ip_data).json()

base_url="https://api.open-meteo.com/v1/forecast?"
geo="latitude="+str(geo_data["lat"])+"&longitude="+str(geo_data["lon"])
tzone="timezone=auto"
unit="temperature_unit=fahrenheit"
status="daily=precipitation_probability_max" + "&" + "current=temperature_2m"
url=base_url+geo+'&'+tzone+'&'+unit+'&'+status

def getInfo():
	return requests.get(url).json()

def drawToday(cdate, draw):
	month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	msg1 = month[int(cdate[1]) - 1]
	msg2 = cdate[2]
	text(draw, (0, 0), msg1, fill="white", font=proportional(LCD_FONT))
	text(draw, (20, 0), msg2, fill="white", font=proportional(LCD_FONT))

def drawMessage():
	global info_loop
	info_loop = True
	now = datetime.now()
	info = getInfo()
	with canvas(device2) as draw2:
		currentDate = info["current"]["time"].split("T")[0].split("-")
		drawToday(currentDate, draw2)
	while info_loop:
		t = datetime.now()
		if t >= now + timedelta(minutes=1):
			info = getInfo()
			now = t
		with canvas(device2) as draw2:
			currentDate = info["current"]["time"].split("T")[0].split("-")
			drawToday(currentDate, draw2)
			time.sleep(5)
			currentTemp = "TEMP: " + str(info["current"]["temperature_2m"]) + "F"
			dailyPrecip = "PoP: " + str(info["daily"]["precipitation_probability_max"][0]) + "%"
			msg = currentTemp + "     " + dailyPrecip
			show_message(device2, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.04)
	device2.cleanup()
	print("INFO END")

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGINT, signal_term_handler)

clock = threading.Thread(target=drawTime)
info = threading.Thread(target=drawMessage)

clock.start()
info.start()

clock.join()
info.join()

print("DONE")
