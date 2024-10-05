import pandas as pd
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO)


class SQLSchemaGenerator:
    def __init__(self, table_name='my_table'):
        """
        Initializes the SQLSchemaGenerator with a table name.

        Args:
            table_name (str, optional): The name of the SQL table. Defaults to 'my_table'.
        """
        self.table_name = table_name

    def write_query_file(self, query, query_file_path='query.sql'):
        """
        Writes a SQL query to a file, ensuring that the directories in the path exist.

        Args:
            query (str): The SQL query to be written to the file.
            query_file (str, optional): Path to the file where the query should be written. Defaults to 'query.sql'.
        """
        # Ensure the directory for the file exists
        dir_name = os.path.dirname(query_file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        # Write the query to the specified file
        with open(query_file_path, 'w') as f:
            f.write(query)
        
        logging.info(f"Query written to {query_file_path}")

    def infer_sql_type(self, dtype, col_values=None):
        """
        Infers the corresponding SQL data type for a given pandas dtype.

        Args:
            dtype (numpy.dtype): The data type of the pandas DataFrame column.
            col_values (pandas.Series, optional): The values of the column for range checking. Defaults to None.

        Returns:
            str: The inferred SQL data type as a string. Possible values include "SMALLINT", "INTEGER", 
            "BIGINT", "FLOAT", "BOOLEAN", "TIMESTAMP", or "TEXT".
        """
        logging.info(f"Infering SQL type for {dtype}")

        if np.issubdtype(dtype, np.integer):
            if col_values is not None:
                min_val = col_values.min()
                max_val = col_values.max()
                if min_val >= -32768 and max_val <= 32767:
                    return "SMALLINT"
                elif min_val >= -2147483648 and max_val <= 2147483647:
                    return "INTEGER"
                else:
                    return "BIGINT"
            else:
                return "INTEGER"

        elif np.issubdtype(dtype, np.floating):
            return "FLOAT"
        elif np.issubdtype(dtype, np.bool_):
            return "BOOLEAN"
        elif np.issubdtype(dtype, np.datetime64):
            return "TIMESTAMP"
        else:
            return "TEXT"

    def generate_schema(self, df, query_file_path='sql/schema.sql', return_query=False):
        """
        Generates a SQL schema for a given pandas DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame for which the schema is to be generated.

        Returns:
            str: A string containing the SQL statement to create the table with the inferred 
            column types.
        """
        logging.info(f"Generating schema for {self.table_name}")
        columns = []
        for col in df.columns:
            col_type = self.infer_sql_type(df[col].dtype, df[col])  # Pass column values
            columns.append(f'"{col}" {col_type}')
        schema = f"CREATE TABLE IF NOT EXISTS {self.table_name} (\n" + ",\n".join(columns) + "\n);"

        self.write_query_file(schema, query_file_path)
        if return_query:
            return schema


    def generate_seed_data(self, df, query_file_path='sql/seed_data.sql', return_query=False):
        """
        Generates SQL insert statements to seed data into a SQL table.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data to be inserted.

        Returns:
            str: A string containing multiple SQL insert statements to seed the data into the table.
        """
        logging.info(f"Generating seed data for {self.table_name}")
        insert_statements = []
        for _, row in df.iterrows():
            values = []
            for value in row:
                if pd.isna(value):
                    values.append("NULL")
                elif isinstance(value, str):
                    values.append(f"'{value.replace('\'', '\'\'')}'")
                elif isinstance(value, pd.Timestamp):
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))
            insert_statements.append(
                f"INSERT INTO {self.table_name} VALUES (" + ", ".join(values) + ");")
        seed_data = "\n".join(insert_statements)
        self.write_query_file(seed_data, query_file_path)
        if return_query:
            return seed_data