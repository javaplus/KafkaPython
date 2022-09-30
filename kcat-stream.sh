#/bin/bash
kafkacat -b pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 \
-X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN \
-X sasl.username=<username>  -X sasl.password=<password>  \
-X auto.offset.reset=end -o end -G copier_group \
-C -t barry -K: -u | kafkacat -b 192.168.8.20:9092,192.168.8.10:9092,192.168.8.30:9092 \
-v -P -t colors -K:
