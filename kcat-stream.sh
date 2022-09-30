#/bin/bash
kafkacat -b pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 \
-X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN \
-X sasl.username=4ANWP4VTF6T52W4Z  -X sasl.password=HDMmqu2NwVumqYWpGB9F7OONxeS2F5vXuPhcae16coLJSFTXKaAZuggYWbQbHziy  \
-X auto.offset.reset=end -o end -G copier_group \
-C -t barry -K: -u | kafkacat -b 192.168.8.20:9092,192.168.8.10:9092,192.168.8.30:9092 \
-v -P -t colors -K:
