import board
import neopixel
import sys

from confluent_kafka import Consumer, KafkaError, TopicPartition


if len(sys.argv)!=2:
  raise ValueError('Provide Partition as argument')
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
    'bootstrap.servers': '192.168.1.128:9092',
    'group.id': 'broker2',
    'client.id': 'pi-broker2',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}
partition = sys.argv[1]
print("partition:" + partition)
c = Consumer(settings)
c.assign([TopicPartition('barry',int(partition))])
# c.subscribe(['barry'])
try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            msgvalue= msg.value().decode('utf-8')
            print('Received message: {0}'.format(msgvalue))
            print("Hello from here")
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
            print("Doned!!!!!")
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            print('End of partition reached {0}/{1}'
                  .format(msg.topic(), msg.partition()))
        else:
            print('Error occured: {0}'.format(msg.error().str()))

except KeyboardInterrupt:
    pass

finally:
    c.close()
