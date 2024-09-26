import os
from dotenv import load_dotenv

load_dotenv()


def get_database_credentials():
    """
    Retrieve database credentials from environment variables.

    This function loads database credentials stored in environment variables 
    and returns them in a dictionary format. The environment variables should 
    be set in a `.env` file or directly in the system environment.

    Returns:
        dict: A dictionary containing the following database connection parameters:
            - 'dbname' (str or None): The name of the database.
            - 'user' (str or None): The username to connect to the database.
            - 'password' (str or None): The password for the database user.
            - 'host' (str or None): The host address of the database server.
            - 'port' (str or None): The port number on which the database server is running.
    """
    return {
        'dbname': os.getenv('DBNAME'),
        'user': os.getenv('DBUSER'),
        'password': os.getenv('DBPASS'),
        'host': os.getenv('DBHOST'),
        'port': os.getenv('DBPORT')
    }
