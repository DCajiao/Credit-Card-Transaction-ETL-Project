from json import dumps, loads
from kafka import KafkaProducer, KafkaConsumer
import pandas as pd


def kafka_producer(row):
    """
    This function sends a message to a Kafka topic.
    Every message is a row from a DataFrame converted to a dictionary with encoding utf-8.
    Kafka-dashboard it's the channel to send the messages.
    """
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=['localhost:9092'],
    )

    message = row.to_dict()
    producer.send('kafka-dashboard', value=message)
    print("Message sent")

def kafka_consumer():
    """
    This function can be deleted for the conneting to PowerBI. This code is to work locally.
    """
    consumer = KafkaConsumer(
        'kafka-happiness',
        enable_auto_commit=True,
        group_id='my-group-1',
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        # cambiar puerto, por el servidor de powerbi y la manera en que se recibe el mensaje
        bootstrap_servers=['localhost:9092']
    )

    for message in consumer:
        df = pd.json_normalize(data=message.value)
        """
        conexion to power BI
        """