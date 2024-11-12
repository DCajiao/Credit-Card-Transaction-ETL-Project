import logging 
import requests
import pandas as pd
import time

from src.connections.db import DB
from src.utils.kafka import kafka_producer

logging.basicConfig(level=logging.INFO)

def get_api_data():
    """
    Retrieves data from a specified API endpoint and returns it as a DataFrame.

    The function sends a GET request to an API that provides data related to
    U.S. states' population. The response is then converted into a pandas DataFrame
    for further processing. If the request fails or the data cannot be processed,
    an error is logged, and the function returns None.

    Returns:
        pd.DataFrame: A DataFrame containing the API data if the request is successful.
                    Returns None if an error occurs.
    """
    API_URL = "https://api-world-population-etl-project.onrender.com/api/v1/data/usa/states"
    try: 
        response = requests.get(API_URL)
        data = response.json()
        df = pd.DataFrame(data)
        logging.info("✔ Successfully got data from API")
        return df
    except Exception as e:
        logging.error(f"✖ Error getting data from API: {e}")
        return None

def get_db_data():
    """
    Retrieves data from a database and returns it as a DataFrame.

    This function establishes a connection to a PostgreSQL database using
    a custom `DB` class. It executes a query to retrieve the first 500,000
    records from the `raw_table` table and returns the result as a DataFrame.
    If the query or connection fails, an error is logged, and the function returns None.

    Returns:
        pd.DataFrame: A DataFrame containing the retrieved database data if successful.
                    Returns None if an error occurs.
    """
    try:
        db = DB()
        df = db.execute_with_query("SELECT * FROM raw_table LIMIT 500000;", fetch_results=True)
        logging.info("✔ Successfully got data from database")
        return df
    except Exception as e:
        logging.error(f"✖ Error getting data from database: {e}")
        return None
    
def get_sample_clean_data():
    """
    Retrieves a sample of cleaned data from a database and returns it as a DataFrame.

    This function establishes a connection to a PostgreSQL database using
    a custom `DB` class. It executes a query to retrieve the first 100 records
    from the `is_fraud` column in the `fact_T_transation_dim` table and returns the result as a DataFrame.
    If the query or connection fails, an error is logged, and the function returns None.

    Returns:
        pd.DataFrame: A DataFrame containing the retrieved database data if successful.
                    Returns None if an error occurs.
    """
    try:
        db = DB()
        result = db.execute_with_query("SELECT * FROM raw_table LIMIT 500000;", fetch_results=True)
        df = pd.DataFrame(result)  # Ensure this matches the data structure
        logging.info("✔ Successfully got sample data from database and sent to Power BI")
        for index, row in df.iterrows():
            kafka_producer(row)
            time.sleep(1)

    except Exception as e:
        logging.error(f"✖ Error getting sample data from database: {e}")
        return None