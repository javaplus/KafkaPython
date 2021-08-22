import subprocess
process = subprocess.run(["/opt/kafka/kafka_2.13-2.8.0/bin/kafka-topics.sh", "--bootstrap-server", "192.168.1.120:9092","--topic", "barry","--describe"],capture_output=True,text=True)
print("return code" + str(process.returncode))
print("stdout=" + process.stdout)
