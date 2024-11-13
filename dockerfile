FROM apache/airflow:2.10.2

RUN pip install --no-cache-dir us kafka-python-ng six
