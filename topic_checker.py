import board
import neopixel
import subprocess
import sys
import time
import os
import logging

logging.basicConfig(filename='/home/pi/logs/topic_checker.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s %(message)s')
topic_name = "colors"


def logMessage(message):
    logging.info(message)


def get_partition_and_leader(topic_string):
    partitionIndex = topic_string.find("Partition:")
    partitionValue = "-1"
    logMessage("PartitionIndex=")
    logMessage(partitionIndex)
    leaderIndex = topic_string.find("Leader:")
    leaderValue = "-1"
    if partitionIndex > -1:
        partitionIndex += 10
        partitionValue = topic_string[partitionIndex:partitionIndex + 3].strip()
    if partitionIndex > -1:
        leaderIndex += 7
        leaderValue = topic_string[leaderIndex:leaderIndex + 3].strip()

    return {"partition": partitionValue, "leader": leaderValue}


def launch_consumer(partition):
    logMessage("launching consumer for partition:" + partition)
    consumer_process = subprocess.Popen(["python3", "/home/pi/consumer.py", partition], stdout=log_file,
                                        stderr=subprocess.STDOUT)
    return consumer_process

num_of_leds = 8
pixels = neopixel.NeoPixel(board.D18, num_of_leds,brightness=0.1)

def clear_bar():
    for x in range(num_of_leds):
        pixels[x] = (0, 0, 0)


def open_log_file(logfilepath):
    return open(logfilepath, mode='w')


def get_kafka_home():
    kafka_home = os.environ['KAFKA_HOME']
    logMessage(kafka_home)
    return kafka_home


if __name__ == '__main__':

    my_leader = "1"

    kafka_home = get_kafka_home()
    if not kafka_home:
        raise ValueError('Provide path to kafka install as argument')
    kafka_topic_command = kafka_home + "bin/kafka-topics.sh"
    logMessage("Kafka topic command =" + kafka_topic_command)
    consumer_process_launched = False
    partition_found_here = False
    log_file = open_log_file("/home/pi/consumer.log")
    currently_watched_partition = -999

    while True:
        # start checking if kafka topic partition is on this leader.
        process = subprocess.run(
            [kafka_topic_command, "--bootstrap-server", "192.168.8.10:9092,192.168.8.20:9092,192.168.8.30:9092",
             "--topic", topic_name, "--describe"], capture_output=True, text=True)

        logMessage("return code" + str(process.returncode))
        logMessage("stdout=")
        # logMessage(process.stdout)
        lines = process.stdout.splitlines()
        for line in lines:
            logMessage("line:" + line)
            part_leader = get_partition_and_leader(line)
            partition = part_leader.get("partition")
            leader = part_leader.get("leader")
            if (leader == my_leader):
                logMessage("leader is here!!!!!!!!!!!!")
                logMessage("partition to watch:" + partition)
                partition_found_here = True
                break
            else:
                partition_found_here = False
        if partition_found_here:
            if not consumer_process_launched:
                logMessage("launching consumer to watch partition" + str(partition))
                consumer_process_to_watch = launch_consumer(partition)
                currently_watched_partition = partition
                consumer_process_launched = True
            elif currently_watched_partition != partition:
                # Shutdown process because partition changed
                logMessage("Killing current consumer because partition changed")
                clear_bar()
                consumer_process_to_watch.terminate()
                consumer_process_to_watch.kill()
                consumer_process_launched = False
        elif consumer_process_launched:
            clear_bar()
            consumer_process_to_watch.terminate()
            consumer_process_to_watch.kill()
            consumer_process_launched = False
        time.sleep(1)  # wait 1 sec before checking again
