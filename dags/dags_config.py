from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import  timedelta

import extract_functions as extract 
import transform_functions as transform
import load_functions as load


# Set the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'start_date':days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}


# Create the DAG
dag = DAG(
    'ETL-pipeline-credit_card_transactions',
    default_args=default_args,
    description='DAG to process credit card transactions',
    schedule_interval='@daily',
    tags=['project']
)

api_connection = PythonOperator(
    task_id='api_get',
    python_callable=extract.get_api_data,
    dag=dag
)

db_connection = PythonOperator(
    task_id='db_get',
    python_callable=extract.get_db_data,
    dag=dag
)

merge_data = PythonOperator(
    task_id='data_merge',
    python_callable=transform.merge_data,
    provide_context=True,
    dag=dag
)

dimensional_model = PythonOperator(
    task_id='dimensional_model',
    python_callable=transform.dimensional_model,
    provide_context=True,
    dag=dag
)

create_queries = PythonOperator(
    task_id='create_queries',
    python_callable=load.create_sql_queries,
    provide_context=True,
    dag=dag,
)

upload_queries = PythonOperator(
    task_id='upload_queries',
    python_callable=load.upload_queries_to_db,
    provide_context=True,
    dag=dag
)

# Set the task dependencies
api_connection >> merge_data
db_connection >> merge_data
merge_data >> dimensional_model
dimensional_model >> create_queries
create_queries >> upload_queries