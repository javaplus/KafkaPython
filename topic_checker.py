import subprocess

def get_partition_and_leader(topic_string):
    partitionIndex = topic_string.find("Partition:")
    partitionValue = "-1"
    print("PartitionIndex=")
    print(partitionIndex)
    leaderIndex = topic_string.find("Leader:")
    leaderValue = "-1"
    if partitionIndex > -1:
        partitionIndex+=10
        partitionValue = topic_string[partitionIndex:partitionIndex+3].strip()
    if partitionIndex > -1:
        leaderIndex+=7
        leaderValue = topic_string[leaderIndex:leaderIndex+3].strip()


    return {"partition": partitionValue, "leader": leaderValue}

process = subprocess.run(["/opt/kafka/kafka_2.13-2.8.0/bin/kafka-topics.sh", "--bootstrap-server", "192.168.1.120:9092","--topic", "barry","--describe"],capture_output=True,text=True)
#process = subprocess.run(["/opt/kafka/kafka_2.13-2.8.0/bin/kafka-topics.sh", "--bootstrap-server", "192.168.1.120:9092","--topic", "barry","--describe"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
print("return code" + str(process.returncode))
print("stdout=")
#print(process.stdout)
lines = process.stdout.splitlines()
for line in lines:
  print("line:" + line)
  part_leader = get_partition_and_leader(line)
  partition = part_leader.get("partition")
  leader = part_leader.get("leader")
  if(leader=="0"):
    print("leader is here!!!!!!!!!!!!")
    print("partition to watch:" + partition)

