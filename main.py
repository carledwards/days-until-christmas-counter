import machine, ssd1306
from machine import Pin
from machine import RTC
from segments import Seg14x4
import network
import ntptime
import time
import utime

def calc_days_until_christmas(year, month, day, hour):
    day -= (1 if hour < 8 else 0) # convert UTC -> PST
    today = utime.mktime([year, month, day, 0, 0, 0, 0, 0])
    if month == 12 and day > 25:
        year += 1
    christmas = utime.mktime([year, 12, 25, 0, 0, 0, 0, 0])
    days_until_christmas = (christmas - today) // (60*60*24)
    return days_until_christmas

i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4))

# setup the OLED display
# pull the OLED_RST pin HIGH
oled_rst = Pin(16, Pin.OUT)
oled_rst.value(1)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# setup the LED display
seg = Seg14x4(i2c)
seg.brightness = 1

# connecting to the wifi
oled.text('connecting to',0,0)
oled.text('wifi',0,10)
oled.show()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect('<<wifi_ssid>>', '<<wifi_password>>')

# wait until the wifi is connected
while not sta.isconnected():
    time.sleep(1)

# Show the static screen on the OLED
oled.fill(0)
oled.text('  Days until', 0, 20)
oled.text('  Christmas:', 0, 40)
oled.show()

while True:
    try:
        # update the time from the internet
        ntptime.settime()

        # calculate the days remaining from the current time
        now = utime.localtime() # UTC time
        days_until_christmas = calc_days_until_christmas(now[0],now[1],now[2],now[3])

        # show the days until Christmas on the LED display
        seg.print(days_until_christmas if days_until_christmas > 0 else "Zero")
        seg.show()

        # update every 1 minute
        time.sleep(60)
    except:
        # sometimes ntptime doesn't work (i.e. times out)
        print("got an error")
        time.sleep(5)
