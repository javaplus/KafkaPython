from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions

a = AdminClient({'bootstrap.servers': '192.168.8.10:9092'})
topic_name = "colors"

partitions = NewPartitions("test", 1, )


def create_second_partition(a):
    """ create partitions """
    new_parts = [NewPartitions(topic_name, 2, [[1, 2]])]
    fs = a.create_partitions(new_parts, validate_only=False)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Additional partitions created for topic {}".format(topic))
        except Exception as e:
            print("Failed to add partitions to topic {}: {}".format(topic, e))


def create_third_partition(a):
    """ create partitions """
    new_parts = [NewPartitions(topic_name, 3, [[2, 0]])]
    fs = a.create_partitions(new_parts, validate_only=False)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Additional partitions created for topic {}".format(topic))
        except Exception as e:
            print("Failed to add partitions to topic {}: {}".format(topic, e))


def delete_topic(a, topic):
    """ delete topics """
    fs = a.delete_topics([topic], operation_timeout=30)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} deleted".format(topic))
        except Exception as e:
            print("Failed to delete topic {}: {}".format(topic, e))





def create_topic(a):
    new_topics = [NewTopic(topic_name, num_partitions=1, replication_factor=2)]
    # Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability.
    # Call create_topics to asynchronously create topics. A dict
    # of <topic,future> is returned.
    fs = a.create_topics(new_topics)
    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))

def test(topics):

    myTopic = topics[0::2]
    print(myTopic)
    myTopic2 = topics[1::2]
    print(myTopic2)
    for topic, new_total_count in zip(topics[0::2], topics[1::2]):
        print(topic)
        print(new_total_count)

#test(["test","1","newtopic","2"])

#delete_topics(a,["test"])
#create_topic()
#topics = ["test"]
create_second_partition(a)
