import logging
import requests
import pandas as pd
import os

from src.connections.db import DB
from src.utils.pysqlschema import SQLSchemaGenerator
from src.utils.kafka import kafka_consumer

logging.basicConfig(level=logging.INFO)


def load_data_to_db(**kwargs):
    """
    Loads merged data into a specified table in the database.

    This function retrieves a merged DataFrame from XCom (shared between Airflow tasks),
    connects to the database, and creates the target table if it doesn't exist.
    The data is then loaded into the table using a custom database class.
    
    Args:
        kwargs (dict): Contains task instance information provided by Airflow for XCom retrieval.

    Returns:
        None
    """
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='data_merge')
    
    db = DB()
    db.connect()
    db.execute_with_query("CREATE TABLE IF NOT EXISTS merged_table (state VARCHAR(255), population INT);")
    db.load_data_to_table(df, 'merged_table')
    db.close()
    logging.info("✔ Successfully loaded data to database")
    
    return None

def create_sql_queries(**kwargs):
    """
    Generates SQL schema and seed data files for each DataFrame in a dictionary.

    This function retrieves a dictionary of DataFrames from XCom, creates a SQL schema and
    seed data file for each DataFrame using `SQLSchemaGenerator`, and saves the files
    to a specified directory. Each table's schema and seed file paths are logged and returned.

    Args:
        kwargs (dict): Contains task instance information provided by Airflow for XCom retrieval.

    Returns:
        list: A list of file paths to the generated schema and seed data SQL files.
    """
    ti = kwargs['ti']
    dfs_dict = ti.xcom_pull(task_ids='dimensional_model')
    
    os.makedirs('sql', exist_ok=True)

    tables_to_clean = ['category_dim', 'client_dim', 'date_dim', 'fact_t_transation_dim', 'job_dim', 'location_dim', 'merchant_dim']
    try:
        for table in tables_to_clean:
            logging.info(f"🪄Cleaning table {table}")
            query = f"DELETE FROM {table};"
            db = DB()
            db.execute_with_query(query, fetch_results=False)
            logging.info(f"✔ Table {table} cleaned")
    except Exception as e:
        logging.error(f"✖ Error cleaning tables: {e}")

    queries_list = []

    for table_name, df in dfs_dict.items():
        # Start the generator for each DataFrame
        generator = SQLSchemaGenerator(table_name=table_name)

        # Set the paths for the schema and seed data files
        schema_file_path = os.path.join('sql', f"{table_name}_schema.sql")
        seed_data_file_path = os.path.join('sql', f"{table_name}_seed_data.sql")

        # Add the paths to the list
        queries_list.append(schema_file_path)
        queries_list.append(seed_data_file_path)

        # Generate and save the schema and data files
        generator.generate_schema(df, schema_file_path)
        generator.generate_seed_data(df, seed_data_file_path)

        logging.info(f"🪄Files generated for {table_name}:")
        logging.info(f"🪄 - Schema: {schema_file_path}")
        logging.info(f"🪄 - Seed data: {seed_data_file_path}")
    
    return queries_list

def upload_queries_to_db(**kwargs):
    """
    Executes SQL queries in batch mode from a list of files, loading data into the database.

    This function retrieves a list of SQL file paths from XCom, connects to the database,
    and executes each query file in batches for efficient loading. Each file's successful
    upload is logged. The database connection is closed upon completion.

    Args:
        kwargs (dict): Contains task instance information provided by Airflow for XCom retrieval.

    Returns:
        None
    """
    ti = kwargs['ti']
    queries_list = ti.xcom_pull(task_ids='create_queries')
    
    db = DB()
    db.connect()
    
    for query_file in queries_list:
        db.execute_in_batches(query_file, batch_size=20000)
        logging.info(f"✔ Successfully uploaded {query_file} to database")
    
    db.close()
    logging.info("🪄 Successfully uploaded queries to database")
    return None

def consumer_execution():
    """
    Consumes messages from a Kafka topic and inserts them into a PostgreSQL database.
    """
    try:
        # Eliminar todos los registros de la tabla data_streaming
        db = DB()
        db.execute_with_query("DELETE FROM data_streaming;", fetch_results=False)
        kafka_consumer()

    except Exception as e:
        logging.error(f"✖ Error consuming messages from Kafka: {e}")  
    return None