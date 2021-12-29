#!/bin/bash
/opt/kafka/kafka_2.13-2.8.0/bin/kafka-leader-election.sh --bootstrap-server 192.168.8.10:9092 --partition 0 --topic colors --election-type PREFERRED
