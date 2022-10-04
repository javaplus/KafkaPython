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


#### Reset Streams application

```
/opt/kafka/kafka_2.13-2.8.0/bin/kafka-streams-application-reset.sh --zookeeper 192.168.8.10:2181 --bootstrap-servers 192.168.8.10:9092 --application-id count_buttons_processor

```

# Systemd stuff to setup Kafka:

https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/

systemctl enable systemd-networkd-wait-online.service

systemctl enable systemd-networkd.service

```
[Unit]
Requires=zookeeper.service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=kafka
ExecStart=/bin/sh -c '/opt/kafka/kafka_2.13-2.8.0/bin/kafka-server-start.sh /opt/kafka/kafka_2.13-2.8.0/config/server.properties > /opt/kafka/kafka_2.13-2.8.0/kafka.log 2>&1'
ExecStop=/opt/kafka/kafka_2.13-2.8.0/bin/kafka-server-stop.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Service locations
Services are located either: /etc/systemd/system  or /lib/systemd/system

#### Custom Services
##### On Brokers:
- zookeeper service (broker 0 only)
- kafka service
- topic_checker service : for seeing which broker partition is on and starting and stopping consumer

##### On Consumers:

- kafka-consumer service: for getting messages and controlling lights.
-

### Network Configuration:

###### get routing table
```
sudo ip route
```
 - ip routing to allow brokers to call out through WAN:
```
sudo ip route del default via 192.168.8.1
```

 - This disables the routing traffic through the internal networks gateway and will cause it to route external calls through the WAN gateway
 - or 
 ```
 sudo ip route del default dev eth0
 ```


## LIBRD Kafka

THis library is used for confluent python libarary to actually interact with kafka.
It seems that the version of this you can just "apt install" does not work on the Raspberry Pis.
So, you have to build it yourself on the raspbery pi from the source.

Had to clone the repo on the Pi's and build it and install it following the instructions from this repo.
https://github.com/edenhill/librdkafka

It can take quite some time to build and install on the PI's especially the Pi Zeros!

Had an issue where I was getting this error on a consumer:
```
pi@KafkaBroker1:~ $ sudo python3 consumer.py 1
Traceback (most recent call last):
  File "consumer.py", line 4, in <module>
    from confluent_kafka import Consumer, KafkaError, TopicPartition
  File "/usr/local/lib/python3.7/dist-packages/confluent_kafka/__init__.py", line 19, in <module>
    from .deserializing_consumer import DeserializingConsumer
  File "/usr/local/lib/python3.7/dist-packages/confluent_kafka/deserializing_consumer.py", line 19, in <module>
    from confluent_kafka.cimpl import Consumer as _ConsumerImpl
ImportError: /usr/local/lib/python3.7/dist-packages/confluent_kafka/cimpl.cpython-37m-arm-linux-gnueabihf.so: undefined symbol: rd_kafka_consumer_group_metadata_write
```
Somehow APT had a version of librdkafka also installed and so I had to remove it using this command:
```sudo apt purge librdkafka1```



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
4. Broker down then rebalance
  - 3 Brokers running, 3 Partition, 1 Producer, 1 consumer.
  - kill one broker and wait for things to rebalance
  - Then messages flow to other brokers where partition was rebalanced.
  - Consumer and producer notices nothing other than a pause while rebalances happens
5.  Consumer down while messages come in
  - 3 Brokers running, 1 or N Partitions, 1 Producer, 1 consumer. (May easier to see with 1 partition)
  - Verify Consumer is receiving messages and then shutdown the consumer
  - Send a few messages and restart the consumer.
  - Consumer should display messages while it was down.
6. Two consumers share the load of messages.


#### Kafka Cat (KCat)

###### Stream from remote topic to local topic

```
kafkacat -b pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 \
-X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN \
-X sasl.username=<ke>  -X sasl.password=<secret>  \
-X auto.offset.reset=end -o end -G copier_group \
-C -t barry -K: -u | kafkacat -b 192.168.8.20:9092,192.168.8.10:9092,192.168.8.30:9092 \
-v -P -t colors -K:
```

###### Get Details:

```
kafkacat -b pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 \
-X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN \
-X sasl.username=<key>  -X sasl.password=<secret>  \
-L
```


########## Links

Confluent Python Library: https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pyclient-admin-newpartitions


