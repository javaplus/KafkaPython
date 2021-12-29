import board
import neopixel
import sys
from confluent_kafka import Consumer, KafkaError, TopicPartition
import logging
import signal,sys


logging.basicConfig(filename='/home/pi/logs/consumer.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')

def logMessage(message):
    logging.info(message)

topic_name = "colors"

if len(sys.argv)!=2:
  raise ValueError('Provide Partition as argument')
num_of_leds = 10
red = (255,0,0)
blue = (0,0,255)
green = (0,255,0)
yellow  = (255,255,0)

pixels = neopixel.NeoPixel(board.D18, num_of_leds,brightness=0.2)

def clear_bar():
    for x in range(num_of_leds):
        pixels[x] = (0, 0, 0)
def indicate_partition(partition_number):
    logMessage("in indicate_partition:"+str(partition_number))
    myrange=range(int(partition_number)+1)
    for index in myrange:
        pixels[index] = green
        logMessage("making indexGreen:" + str(index))

def termination_handler(signum, frame):
  logMessage("I'm shutting down vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvVVVVVVVVVVVVVVVVV")
  clear_bar()
  sys.exit(0)

signal.signal(signal.SIGTERM, termination_handler)
partition = sys.argv[1]

clear_bar()
indicate_partition(partition)

current_index=0

settings = {
    'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
    'group.id': 'broker0',
    'client.id': 'pi-broker0',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}

logMessage("partition:" + partition)
c = Consumer(settings)
c.assign([TopicPartition(topic_name, int(partition))])
# c.subscribe(['barry'])
try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            msgvalue = msg.value().decode('utf-8')
            logMessage('Received message: {0}'.format(msgvalue))
            logMessage("Hello from here")
            if (current_index >= num_of_leds):
                clear_bar()
                current_index = 0
            pixels[current_index] = tuple(map(int,msgvalue.split(",")))
            current_index = current_index + 1
            logMessage("Doned!!!!!")
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            logMessage('End of partition reached {0}/{1}'
                  .format(msg.topic(), msg.partition()))
        else:
            logMessage('Error occured: {0}'.format(msg.error().str()))

except KeyboardInterrupt:
    pass

finally:
    c.close()
