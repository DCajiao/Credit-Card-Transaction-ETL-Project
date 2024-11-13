import pandas as pd
import us
import logging

logging.basicConfig(level=logging.INFO)

def merge_data(**kwargs):
    """
    Merges API and database data into a single DataFrame based on state information.

    This function retrieves two DataFrames (one from the API and one from the database)
    using Airflow's XCom, merges them on the state-related columns, and returns the merged
    DataFrame. If either DataFrame is missing, an exception is raised.

    Args:
        kwargs (dict): Contains task instance information provided by Airflow for XCom retrieval.

    Returns:
        pd.DataFrame: A merged DataFrame containing both API and database data.

    Raises:
        ValueError: If either the API data or the DB data is not available.
    """
    ti = kwargs['ti']
    df_api = ti.xcom_pull(task_ids='api_get')
    df_db = ti.xcom_pull(task_ids='db_get')
    
    if df_api is None or df_db is None:
        raise ValueError("API data or DB data not available for merging.")
    
    df_api.columns = [col.lower() for col in df_api.columns.to_list()]
    df_merged = df_db.merge(df_api, left_on='state', right_on='state_abbreviation', how='left')
    logging.info(f"🪄 Merged data from API and DB. Shape: {df_merged.shape}")
    
    return df_merged

def get_fips_from_usps(usps_code):
    """
    Retrieves the FIPS code for a given USPS state abbreviation.

    This helper function uses the `us` library to lookup the FIPS code for
    a state based on its USPS code.

    Args:
        usps_code (str): The USPS state code (e.g., 'CA' for California).

    Returns:
        str or None: The FIPS code as a string if found; otherwise, None.
    """
    state = us.states.lookup(usps_code)
    return state.fips if state else None

def dimensional_model(**kwargs):
    """
    Creates a dimensional model from the merged transactional DataFrame.

    This function performs various transformations on the merged DataFrame retrieved
    via XCom, including adding new columns for date and state information, creating 
    unique IDs for categories, jobs, and locations, and splitting date-time data into 
    separate components. The function outputs a dictionary of dimension DataFrames 
    for further analysis and loading.

    Args:
        kwargs (dict): Contains task instance information provided by Airflow for XCom retrieval.

    Returns:
        dict: A dictionary containing DataFrames for each dimension in the model, with keys 
              corresponding to each dimension's name.
    """
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='data_merge')
    
    # 1. Transformations and necessary column creations
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    df['trans_date_id'] = df['trans_date_trans_time'].dt.strftime('%Y%m%d').astype(int)
    df['state_id'] = df['state_abbreviation'].apply(get_fips_from_usps)
    
    # Map categories and jobs to unique IDs
    df['category_id'] = df['category'].factorize()[0]
    df['job_id'] = df['job'].factorize()[0] + 1010

    # Generate unique location IDs
    df['location_id'] = (df['state_id'].astype(str) + 
                                df['zip'].astype(str) + 
                                df.groupby(['state_id', 'zip']).cumcount().add(1).astype(str))
    
    # Split datetime column into additional components
    df['date'] = df['trans_date_trans_time'].dt.date
    df['year'] = df['trans_date_trans_time'].dt.year
    df['month'] = df['trans_date_trans_time'].dt.month
    df['quarter'] = df['trans_date_trans_time'].dt.quarter
    df['hour'] = df['trans_date_trans_time'].dt.hour

    # Ensure merch_zipcode is an integer type for consistency
    df['merch_zipcode'] = df['merch_zipcode'].astype(int)
    
    # 2. Create dimension DataFrames
    dimensions = {
        "fact_T_transation_dim": df[['trans_num', 'is_fraud', 'amt', 'hour', 'trans_date_id', 'trans_date_trans_time', 'cc_num', 'location_id', 'merch_zipcode']],
        "category_dim": df[['category_id', 'category']].drop_duplicates(),
        "merchant_dim": df[['merch_zipcode', 'merchant', 'category_id']].drop_duplicates(),
        "client_dim": df[['cc_num', 'first', 'last', 'gender', 'job_id', 'age']].drop_duplicates(),
        "job_dim": df[['job_id', 'job']].drop_duplicates(),
        "date_dim": df[['trans_date_id', 'date', 'month', 'year', 'quarter']].drop_duplicates(),
        "location_dim": df[['location_id', 'street', 'lat', 'long', 'zip', 'state_id']].drop_duplicates(),
        "state_dim": df[['state_id', 'state_abbreviation', 'state_name', 'state_population']].drop_duplicates()
    }
    
    return dimensions