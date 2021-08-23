# KafkaPython
Some Kafka Python consumers and providers, plus some other utilities


Good commands for managing Kafka:

/opt/kafka/kafka_2.13-2.8.0/bin/kafka-topics.sh --zookeeper 192.168.1.128:2181 --topic colors --create --partitions 2 --replication-factor 2
/opt/kafka/kafka_2.13-2.8.0/bin/kafka-topics.sh --zookeeper 192.168.1.128:2181 --topic colors --describe
/opt/kafka/kafka_2.13-2.8.0/bin/kafka-leader-election.sh --bootstrap-server 192.168.1.128:9092 --partition 0 --topic colors --election-type PREFERRED
/opt/kafka/kafka_2.13-2.8.0/bin/zookeeper-shell.sh 192.168.1.128:2181 ls /brokers/ids

/opt/kafka/kafka_2.13-2.8.0/bin/kafka-reassign-partitions.sh --bootstrap-server 192.168.1.128:9092 --reassignment-json-file ./assign.json --execute

/opt/kafka/kafka_2.13-2.8.0/bin/kafka-topics.sh --zookeeper 192.168.1.128:2181 --topic colors --alter --partitions 2

journalctl -u topic_checker -b


