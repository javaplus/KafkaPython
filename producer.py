from confluent_kafka import Producer
import socket
import time
import logging

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


logging.basicConfig(filename='/home/pi/logs/producer.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
mylogger = logging.getLogger()

def logMessage(message):
    logging.info(message)


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 8 to be an input pin and set
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 5 to be an input pin and set

delay = .15

# conf = {'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
conf = {'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092',
        'client.id': 'piProducer1',
        'metadata.max.age.ms':'20000'}
topic = 'colors'
producer = Producer(conf,logger=mylogger)

def produceMessage(message):
    if message == "255,0,0":
      producer.produce(topic, key="mymessageisred", value=message)
    else:
      producer.produce(topic, key=message, value=message)
    producer.flush()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logMessage('Starting main')
    while True:
      if GPIO.input(10) == GPIO.HIGH:
        produceMessage("255,0,0")
        logMessage('Sending Red')
        time.sleep(delay)
      if GPIO.input(8) == GPIO.HIGH:
        produceMessage("0,0,255")
        logMessage('Sending blue')
        time.sleep(delay)
      if GPIO.input(16) == GPIO.HIGH:
        produceMessage("255,255,0")
        logMessage('Sending yeloo')
        time.sleep(delay)

