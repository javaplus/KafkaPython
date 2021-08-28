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


# Scenarios:

1. Base line test simple 
  - 3 Brokers running, 1 Partition, 1 Producer, 1 consumer. 
  - Producer sends messages they go to one broker that has the partition and all messages go to single consumer.
2. Messages Split across 2 partitions tests
  - 3 Brokers running, 2 Partitions, 1 Producer, 1 consumer. 
  - Producer sends messages they should split to 2 different Brokers.  2 types of message go to 1 broker and 1 type of message goes to another broker/partition. All messages go to single consumer
3. Messages split across 3 partitions.
  - 3 Brokers running, 3 Partition, 1 Producer, 1 consumer.
  - Producer sends messages they should split to 3 different Brokers.  Messages split across each broker/partition. All messages go to single consumer
4. 3 Brokers running, 3 Partition, 1 Producer, 1 consumer.
  - kill one broker and wait for things to rebalance
  - Then messages flow to other brokers where partition was rebalanced.
  - Consumer and producer notices nothing other than a pause while rebalances happens
5.  3 Brokers running, 1 or N Partitions, 1 Producer, 1 consumer. (May easier to see with 1 partition)
  - Verify Consumer is receiving messages and then shutdown the consumer
  - Send a few messages and restart the consumer.
  - Consumer should display messages while it was down.
6. 
