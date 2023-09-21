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

logging.basicConfig(filename='/home/pi/logs/consumer.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
mylogger = logging.getLogger()
def logMessage(message):
    logging.info(message)

num_of_leds = 10
num_of_plaque_leds = 23
red = (255,0,0)
blue = (0,0,255)
green = (0,255,0)
yellow  = (255,255,0)
noMessage = (2,8,7)
delayMessage = (2,8,6)

sleep_time_seconds = .5
current_index=0

def clear_bar():
    for x in range(num_of_leds):
        pixels[x] = (0, 0, 0)
    current_index=0

pixels = neopixel.NeoPixel(board.D18, num_of_leds + num_of_plaque_leds,brightness=0.10)
clear_bar()

def processMessage(message):
  global sleep_time_seconds
  try:
    tupleMessage =  tuple(map(int,msgvalue.split(",")))

    for i in range(3):
      if(tupleMessage[i] < 0 or tupleMessage[i] > 255):
        logMessage("Message being rejected to high or low")
        return None
      # if special message of 2,8,6 then change sleep time
      if(tupleMessage == delayMessage):
        sleep_time_seconds = .5
        logMessage("Sleeptime=" + str(sleep_time_seconds))
        return None
      elif(tupleMessage == noMessage):
        sleep_time_seconds = 0
        logMessage("Sleeptime=" + str(sleep_time_seconds))
        return None
    return tupleMessage
  except Exception as e:
    logMessage("Exception processing Message:" + str(e))
    return None

settings = {
    'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
    'group.id': 'pie',
    'client.id': 'pie-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'metadata.max.age.ms': 20000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}
button_on = True


def checkButton():
    if GPIO.input(21) == GPIO.HIGH:
        return True
    else:
        return False

def lightNamePlaque():
    pixels.brightness =.1
    totalLeds = num_of_leds + num_of_plaque_leds
    for pixel in range(num_of_leds, totalLeds):
        pixels[pixel] = (255,255,255)

def turnOffNamePlaque():
    totalLeds = num_of_leds + num_of_plaque_leds
    for pixel in range(num_of_leds,totalLeds):
        pixels[pixel] = (0,0,0)
try:
    while True:
        button_on = checkButton()
        if button_on:
            c = Consumer(settings, logger=mylogger)
            c.subscribe(['colors'])
            logMessage("Subscribing to Topic")
            lightNamePlaque()

            while button_on:
                button_on = checkButton()
                msg = c.poll(0.1)
                if msg is None:
                    continue
                elif not msg.error():
                    msgvalue= msg.value().decode('utf-8')
                    logMessage('Received message: {0}'.format(msgvalue))
                    logMessage("Hello from here")
                    if(current_index>=num_of_leds):
                        clear_bar()
                        current_index=0
                    processedMessage = processMessage(msgvalue)
                    if processedMessage is None:
                      continue
                    # after consuming message, pause before displaying
                    time.sleep(sleep_time_seconds)
                    pixels[current_index] = processedMessage
                    current_index = current_index + 1
                    logMessage("Doned!!!!!")
                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    logMessage('End of partition reached {0}/{1}'
                          .format(msg.topic(), msg.partition()))
                else:
                    logMessage('Error occured: {0}'.format(msg.error().str()))

            logMessage("Closing consumer")
            clear_bar()
            turnOffNamePlaque()
            current_index=0
            c.close()
        time.sleep(.15)
except KeyboardInterrupt:
    pass

finally:
    c.close()

