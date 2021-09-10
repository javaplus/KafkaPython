import board
import neopixel
from confluent_kafka import Consumer, KafkaError
import logging

logging.basicConfig(filename='/home/pi/logs/consumer.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
mylogger = logging.getLogger()
def logMessage(message):
    logging.info(message)

num_of_leds = 8
red = (255,0,0)
blue = (0,0,255)
green = (0,255,0)
yellow  = (255,255,0)

def clear_bar():
    for x in range(num_of_leds):
        pixels[x] = (0, 0, 0)

pixels = neopixel.NeoPixel(board.D18, num_of_leds)
clear_bar()


current_index=0

settings = {
    'bootstrap.servers': '192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092',
    'group.id': 'pie',
    'client.id': 'pie-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'metadata.max.age.ms': 20000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}
c = Consumer(settings,logger=mylogger)
c.subscribe(['colors'])
try:
    while True:
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
            if(msgvalue=='red'):
                pixels[current_index] = red
            if(msgvalue=='blue'):
                pixels[current_index] = blue
            if (msgvalue == 'green'):
                pixels[current_index] = green
            if (msgvalue == 'yellow'):
                pixels[current_index] = yellow
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

