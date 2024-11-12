from json import dumps, loads
from kafka import KafkaProducer, KafkaConsumer
import pandas as pd

from src.connections.db import DB
db = DB()
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
    This function consumes messages from a Kafka topic and inserts them into a PostgreSQL database.
    """
    consumer = KafkaConsumer(
        'kafka-dashboard',  # Topic name
        enable_auto_commit=True,
        group_id='my-group-1',
        value_deserializer=lambda m: loads(m.decode('utf-8')),  # Deserialize messages to JSON
        bootstrap_servers=['localhost:9092']
    )
    # SQL query for insertion
    insert_query = """
    INSERT INTO data_streaming (
        "id", "trans_date_trans_time", "cc_num", "merchant", "category", "amt",
        "first", "last", "gender", "street", "city", "state", "zip", "lat",
        "long", "job", "dob", "trans_num", "is_fraud", "merch_zipcode", "age"
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    # Consuming messages and inserting them into the database
    for message in consumer:
        print(f"Received message: {message.value}")  # Print the consumed message
        df = pd.json_normalize(data=message.value)  # Convert the message to a DataFrame

        # Insert each row into the database using the execute_insert method
        for _, row in df.iterrows():
            values = (
                row["id"], row["trans_date_trans_time"], row["cc_num"], row["merchant"],
                row["category"], row["amt"], row["first"], row["last"], row["gender"],
                row["street"], row["city"], row["state"], row["zip"], row["lat"],
                row["long"], row["job"], row["dob"], row["trans_num"], row["is_fraud"],
                row["merch_zipcode"], row["age"]
            )
            
            # Ejecutar la inserción usando la función execute_insert
            try:
                db.execute_insert(insert_query, values)
                print(f"Inserted row into the database: {row['id']}")
            except Exception as e:
                print(f"Error inserting row: {e}")
                continue  # Si hay un error, continuar con el siguiente registro