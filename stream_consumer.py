import json
import board
import neopixel
from confluent_kafka import Consumer, KafkaError
import logging
import time
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

num_of_leds = 127
red = (255,0,0)
blue = (0,0,255)
green = (0,255,0)
yellow  = (255,255,0)
ORDER = neopixel.RGB
current_index=0
color_salt = 95
letter_led_collection = [32, 21, 21, 32, 21]
logging.basicConfig(filename='/home/pi/logs/consumer.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
mylogger = logging.getLogger()
def logMessage(message):
    logging.info(message)

settings = {
    'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
    'group.id': 'pie-4',
    'client.id': 'pie-4',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'metadata.max.age.ms': 20000,
    'default.topic.config': {'auto.offset.reset': 'latest'}
}

def map_color(color_string):
    ledColor = green
    if color_string == "red":
      ledColor = red
    elif color_string == "blue":
      ledColor = blue
    elif color_string == "yellow":
      ledColor = yellow;

    return ledColor

def clear_bar():
    for x in range(num_of_leds):
        pixels[x] = (0, 0, 0)

def redraw_letters(color, count):
    ledColor = map_color(color)
    current_led_index = 0
    for index in range(count):
      ledcount=letter_led_collection[index]
      for x in range(ledcount):
        pixels[current_led_index] = ledColor
        current_led_index+=1
        time.sleep(.05)
        
 def flash_letters(color, count):
    clear_bar()

    if count >  5:
     color_salt = 0
     rainbow_cycle(.0001)
     color_salt = 225
     clear_bar()
     rainbow_cycle(.0001)
     color_salt = 95
     clear_bar()
     rainbow_cycle(.0001)

    else:
     redraw_letters(color, count)


pixels = neopixel.NeoPixel(board.D18, num_of_leds)
clear_bar()


settings = {
    'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
    'group.id': 'pie',
    'client.id': 'pie-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'metadata.max.age.ms': 20000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}

def checkButton():
    if GPIO.input(21) == GPIO.HIGH:
        return True
    else:
        return False
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def rainbow_cycle(wait):
    logMessage("in rainbow cycle")
    #logMessage("color_salt=" + str(color_salt))
    for i in range(num_of_leds):
        pixel_index = (i * 256 // num_of_leds) + color_salt
        pixels[i] = wheel(pixel_index & 255)
    pixels.show()

def processButtonCountMessage(btnCntMsg):
    button_color = btnCntMsg["button"]
    button_count = btnCntMsg["count"]
    logMessage("button count:" + str(button_count))
    flash_letters(button_color, button_count)

    rainbow_cycle(.0001)

try:
    c = Consumer(settings, logger=mylogger)
    c.subscribe(['button_count'])
    logMessage("Subscribing to Topic")
    rainbow_cycle(.0005)

    while True:
        #color_salt+=15
        #if color_salt > 240:
        #   color_salt = 30
        #rainbow_cycle(.0005)
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            msgvalue = msg.value().decode('utf-8')
            logMessage('Received message: {0}'.format(msgvalue))
            parsedJson = json.loads(msgvalue)
            logMessage("button pressed = " + parsedJson["button"])
            processButtonCountMessage(parsedJson)
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            logMessage('End of partition reached {0}/{1}'
                  .format(msg.topic(), msg.partition()))
        else:
            logMessage('Error occured: {0}'.format(msg.error().str()))
except KeyboardInterrupt:
    pass

finally:
    c.close()

