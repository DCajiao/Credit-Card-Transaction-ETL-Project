import pandas as pd
import us
import os
import sys

def process_dataframe(df_sample):
    """
    This function processes the dataframe, performing various transformations and generating dimension tables.
    Args:
        df_sample (DataFrame): Input dataframe.
    Returns:
        dict: Dictionary of dimension dataframes.
    """
    
    # Changing the transaction date to an incremental integer
    df_sample['trans_date_trans_time'] = pd.to_datetime(df_sample['trans_date_trans_time'])
    df_sample['trans_date_id'] = df_sample['trans_date_trans_time'].dt.strftime('%Y%m%d').astype(int)
    
    # Retrieve FIPS code for states using 'us' library
    def get_fips_from_usps(usps_code):
        state = us.states.lookup(usps_code)
        return state.fips if state else None

    df_sample['state_id'] = df_sample['state_abbreviation'].apply(get_fips_from_usps)

    # Creating a unique ID for each category
    category_mapping = {category: idx for idx, category in enumerate(df_sample['category'].unique(), start=0)}
    df_sample['category_id'] = df_sample['category'].map(category_mapping)

    # Creating a unique ID for each job
    job_mapping = {job: idx for idx, job in enumerate(df_sample['job'].unique(), start=1010)}
    df_sample['job_id'] = df_sample['job'].map(job_mapping)

    # Location ID generation by concatenating 'zip', 'state_id', and an incrementing number
    counter = 1
    def generate_unique_id(row):
        nonlocal counter
        unique_id = str(row['state_id']) + str(row['zip']) + str(counter)
        counter += 1
        return unique_id

    df_sample['location_id'] = df_sample.apply(generate_unique_id, axis=1)

    # Function to split the 'trans_date_trans_time' column into multiple new columns
    def split_datetime_column(df):
        df['date'] = pd.to_datetime(df['trans_date_trans_time']).dt.date
        df['year'] = pd.to_datetime(df['trans_date_trans_time']).dt.year
        df['month'] = pd.to_datetime(df['trans_date_trans_time']).dt.month
        df['quarter'] = pd.to_datetime(df['trans_date_trans_time']).dt.quarter
        df['hour'] = pd.to_datetime(df['trans_date_trans_time']).dt.time
        return df

    df_sample = split_datetime_column(df_sample)
    df_sample['merch_zipcode'] = df_sample['merch_zipcode'].apply(lambda x: int(x))

    # Creating dimension dataframes
    fact_T_transation_dim = df_sample[['trans_num', 'is_fraud', 'amt', 'hour', 'trans_date_id', 'trans_date_trans_time', 'cc_num', 'location_id', 'merch_zipcode']]
    category_dim = df_sample[['category_id', 'category']]
    merchant_dim = df_sample[['merch_zipcode', 'merchant', 'category_id']]
    client_dim = df_sample[['cc_num', 'first', 'last', 'gender', 'job_id', 'age']]
    job_dim = df_sample[['job_id', 'job']]
    date_dim = df_sample[['trans_date_id', 'date', 'month', 'year', 'quarter']]
    location_dim = df_sample[['location_id', 'street', 'lat', 'long', 'zip', 'state_id']]
    state_dim = df_sample[['state_id', 'state_abbreviation', 'state_name', 'state_population']]

    return {
        "fact_T_transation_dim": fact_T_transation_dim,
        "category_dim": category_dim,
        "merchant_dim": merchant_dim,
        "client_dim": client_dim,
        "job_dim": job_dim,
        "date_dim": date_dim,
        "location_dim": location_dim,
        "state_dim": state_dim
    }

# This function removes duplicate data from a specific DataFrame using the specified column.
def dim_drop_duplicates(df, col):
    df.drop_duplicates(subset=[col], inplace=True)
    return df

# Removes duplicate data for each dimension before saving the changes to CSV files.
def save_dfs_to_csv(dfs, columns, filenames):
    """
    Apply dim_drop_duplicates on each DataFrame and save as a CSV file in a specific directory.

    Args:
        dfs (list): List of DataFrames to process.
        columns (list): List of column names for dropping duplicates in each DataFrame.
        filenames (list): List of filenames to save the CSVs.
    """
    path_to_data_folder = os.path.join(os.getcwd(), 'data', 'dimensions')

    if not os.path.exists(path_to_data_folder):
        os.makedirs(path_to_data_folder)

    for df, col, filename in zip(dfs, columns, filenames):
        df = dim_drop_duplicates(df, col)
        full_path = os.path.join(path_to_data_folder, filename)
        df.to_csv(full_path, index=False)
        print(f"Saved {filename} to {full_path}")

# Main function that reads the CSV, processes the dataframe, and saves the output CSVs
def main(csv_path):
    """
    Main function to read the CSV, process the dataframe, and save the output CSV files.
    
    Args:
        csv_path (str): Path to the input CSV file.
    """
    # Read the CSV file into a DataFrame
    df_sample = pd.read_csv(csv_path)
    
    # Process the dataframe and create dimensions
    dimensions = process_dataframe(df_sample)
    
    # List of DataFrames
    dfs = [dimensions['category_dim'], dimensions['merchant_dim'], dimensions['client_dim'], dimensions['job_dim'], 
           dimensions['date_dim'], dimensions['location_dim'], dimensions['state_dim']]
    
    # Corresponding columns to check for duplicates
    columns = ['category_id', 'merch_zipcode', 'cc_num', 'job_id', 'trans_date_id', 'location_id', 'state_id']
    
    # Corresponding filenames
    filenames = ['category_dim.csv', 'merchant_dim.csv', 'client_dim.csv', 'job_dim.csv', 
                 'date_dim.csv', 'location_dim.csv', 'state_dim.csv']
    
    # Call the function to process and save each DataFrame
    save_dfs_to_csv(dfs, columns, filenames)

# Example usage: call the main function with the path to your CSV file
if __name__ == "__main__":
    # Provide your CSV file path here
    csv_file_path = 'D:/User/Documents/UAO/6_Semestre/ETL/Project/Credit_Card_ETL_Project/data/sample_credit_card_transactions_api_preprocessed.csv'
    main(csv_file_path)
