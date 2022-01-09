import json
import board
import neopixel
from confluent_kafka import Consumer, KafkaError, TopicPartition, OFFSET_END
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
logging.basicConfig(filename='/home/pi/logs/race.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
mylogger = logging.getLogger()
def logMessage(message):
    logging.info(message)

def map_color(color_string):
  try:
    tupleMessage =  tuple(map(int, color_string.split(",")))

    for i in range(3):
      if(tupleMessage[i] < 0 or tupleMessage[i] > 255):
        logMessage("Message being rejected to high or low")
        return None
    return tupleMessage
  except Exception as e:
    logMessage("Exception processing Message:" + str(e))
    return None


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

# Add one pix for color regardless of count
def add_colors(color):
    ledColor = map_color(color)
    if ledColor is None:
      return
    global current_index
    global num_of_leds
    if current_index == num_of_leds:
        current_index=0
        redraw_letters("0,255,0",5)
        clear_bar()
    pixels[current_index] = ledColor
    current_index+=1
    time.sleep(.01)


pixels = neopixel.NeoPixel(board.D18, num_of_leds)
clear_bar()
redraw_letters("0,255,0",5)
clear_bar()

settings = {
    'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
    'group.id': 'pie4',
    'client.id': 'pie-4',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'metadata.max.age.ms': 20000,
    'default.topic.config': {'auto.offset.reset': 'latest'}
}

def checkButton():
    if GPIO.input(21) == GPIO.HIGH:
        return True
    else:
        return False

def processButtonCountMessage(btnCntMsg):
    button_color = btnCntMsg["button"]
    button_count = btnCntMsg["count"]
    logMessage("button count:" + str(button_count))
    add_colors(button_color)


try:
    c = Consumer(settings, logger=mylogger)
    c.assign([TopicPartition('button_count', 0, OFFSET_END)])
    # c.subscribe(['button_count'])
    logMessage("Subscribing to Topic")

    while True:
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
