from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions
import time
import board
import logging
import time
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


BUTTON_ONE = 22
BUTTON_TWO = 27
GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(BUTTON_ONE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_TWO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

logging.basicConfig(filename='/home/pi/logs/admin.log', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
mylogger = logging.getLogger()


def logMessage(message):
    logging.info(message)
    # print(message)


a = AdminClient({'bootstrap.servers': '192.168.8.10:9092'})
topic_name = "colors"

number_of_partitions = 0


def checkButton(button):
    if GPIO.input(button) == GPIO.HIGH:
        return True
    else:
        return False


def create_second_partition(a):
    """ create partitions """
    new_parts = [NewPartitions(topic_name, 2, [[1, 2]])]
    fs = a.create_partitions(new_parts, validate_only=False)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logMessage("Additional partitions created for topic {}".format(topic))
        except Exception as e:
            logMessage("Failed to add partitions to topic {}: {}".format(topic, e))

            
def create_third_partition(a):
    """ create partitions """
    new_parts = [NewPartitions(topic_name, 3, [[2, 0]])]
    fs = a.create_partitions(new_parts, validate_only=False)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logMessage("Additional partitions created for topic {}".format(topic))
        except Exception as e:
            logMessage("Failed to add partitions to topic {}: {}".format(topic, e))


def delete_topic(a, topic):
    """ delete topics """
    fs = a.delete_topics([topic], operation_timeout=30)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logMessage("Topic {} deleted".format(topic))
        except Exception as e:
            logMessage("Failed to delete topic {}: {}".format(topic, e))


def create_topic(a):
    new_topics = [NewTopic(topic_name, num_partitions=1, replication_factor=-1, replica_assignment=[[0, 1]])]
    # Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability.
    # Call create_topics to asynchronously create topics. A dict
    # of <topic,future> is returned.
    fs = a.create_topics(new_topics)
    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logMessage("Topic {} created".format(topic))
        except Exception as e:
            logMessage("Failed to create topic {}: {}".format(topic, e))


while True:
    button1Down = checkButton(BUTTON_ONE)
    button2Down = checkButton(BUTTON_TWO)
    if number_of_partitions == 1 and button1Down:
        create_second_partition(a)
        number_of_partitions = 2
    elif number_of_partitions == 2 and button2Down:
        create_third_partition(a)
        number_of_partitions = 3
    elif number_of_partitions != 1 and not button1Down and not button2Down:
        delete_topic(a, topic_name)
        number_of_partitions = 1
        time.sleep(3)
        create_topic(a)
    time.sleep(3)


