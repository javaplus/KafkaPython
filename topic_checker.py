import subprocess
import sys
import time
import os

def get_partition_and_leader(topic_string):
    partitionIndex = topic_string.find("Partition:")
    partitionValue = "-1"
    print("PartitionIndex=")
    print(partitionIndex)
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
    print("launching consumer for partition:" + partition)
    consumer_process = subprocess.Popen(["sudo", "python3", "/home/pi/consumer.py", partition],stdout=log_file, stderr=subprocess.STDOUT)
    return consumer_process

def open_log_file(logfilepath):
    return open(logfilepath, mode='w')

def get_kafka_home():
    kafka_home = os.environ['KAFKA_HOME']
    print(kafka_home)
    return kafka_home

if __name__ == '__main__':

    kafka_home = get_kafka_home()
    if not kafka_home:
        raise ValueError('Provide path to kafka install as argument')
    kafka_topic_command = kafka_home + "bin/kafka-topics.sh"
    print("Kafka topic command =" + kafka_topic_command)
    consumer_process_launched = False
    partition_found_here = False
    log_file = open_log_file("/home/pi/consumer.log")

    while True:
        # start checking if kafka topic partition is on this leader.
        process = subprocess.run([kafka_topic_command, "--bootstrap-server", "192.168.1.120:9092",
                                  "--topic", "barry", "--describe"], capture_output=True, text=True)

        print("return code" + str(process.returncode))
        print("stdout=")
        # print(process.stdout)
        lines = process.stdout.splitlines()
        for line in lines:
            print("line:" + line)
            part_leader = get_partition_and_leader(line)
            partition = part_leader.get("partition")
            leader = part_leader.get("leader")
            if (leader == "0"):
                print("leader is here!!!!!!!!!!!!")
                print("partition to watch:" + partition)
                partition_found_here = True
                break
            else:
                partition_found_here = False
        if partition_found_here:
            if not consumer_process_launched:
                consumer_process_to_watch = launch_consumer(partition)
                consumer_process_launched = True
        elif consumer_process_launched:
            consumer_process_to_watch.kill()
            consumer_process_launched = False
        time.sleep(1) # wait 1 sec before checking again
