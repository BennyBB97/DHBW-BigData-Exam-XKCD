# -*- coding: utf-8 -*-

from datetime import datetime
from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.hdfs_operations import HdfsMkdirFileOperator
from airflow.operators.filesystem_operations import CreateDirectoryOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from concurrent.futures import ThreadPoolExecutor

import requests
import os
import json

args = {
    'owner': 'airflow'
}

def get_all_XKCD(i):       
    url = 'https://xkcd.com/' + str(i) + '/info.0.json'
    response = requests.get(url).json()
    year = response.get('year')
    if os.path.exists('/home/airflow/xkcd/raw/' + str(year)) == False:
        os.mkdir('/home/airflow/xkcd/raw/' + str(year))
    with open(f"{'/home/airflow/xkcd/raw/' + str(year)}/{i}.json", 'w') as f:
        json.dump(response, f)

#Requests with threading -> Download from ~10 min to ~9 sec
def main():   
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url).json()
    num_last_xkcd = response.get('num')
    numbers = list(range(1, num_last_xkcd + 1))
    with ThreadPoolExecutor(max_workers=400) as executer:
        executer.map(get_all_XKCD, numbers)
        executer.shutdown(wait=True)


dag = DAG('XKCD_DAG', default_args=args, description='XKCD Comic Dag',
schedule_interval='56 18 * * *',
start_date=datetime(2022, 11, 22), catchup=False, max_active_runs=1)

create_local_import_dir_xkcd = CreateDirectoryOperator(
    task_id ='create_local_import_dir_xkcd',
    path ='/home/airflow',
    directory ='xkcd',
    dag = dag,
)

create_local_import_dir_raw = CreateDirectoryOperator(
    task_id ='create_local_import_dir_raw',
    path ='/home/airflow/xkcd',
    directory ='raw',
    dag = dag,
)

clear_local_import_dir = BashOperator(
    task_id='clear_local_import_dir',
    bash_command='rm -r /home/airflow/xkcd/raw/*',
)

download_xkcd = PythonOperator(
    task_id='download_xkcd',
    python_callable=main,
    dag=dag,
)

create_hdfs_init_file = BashOperator(
    task_id='create_hdfs_init_file',
    bash_command='/home/airflow/hadoop/bin/hadoop fs -touch /user/hadoop/xkcd/raw/init.txt',
)

create_local_init_file = BashOperator(
    task_id='create_local_init_file',
    bash_command='touch /home/airflow/xkcd/raw/init.txt',
)

hdfs_clear_xkcd = BashOperator(
    task_id='hdfs_clear_xkcd',
    bash_command='/home/airflow/hadoop/bin/hadoop dfs -rm -r /user/hadoop/xkcd/raw',
)

hdfs_push_xkcd = BashOperator(
    task_id='hdfs_push_xkcd',
    bash_command='/home/airflow/hadoop/bin/hadoop fs -put /home/airflow/xkcd /user/hadoop',
)

hdfs_create_xkcd_dir = HdfsMkdirFileOperator(
    task_id='hdfs_create_xkcd_dir',
    directory='/user/hadoop/xkcd',
    hdfs_conn_id='hdfs',
    dag=dag,
)

hdfs_create_xkcd_raw_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_xkcd_raw_dir',
    directory='/user/hadoop/xkcd/raw',
    hdfs_conn_id='hdfs',
    dag=dag,
)

pyspark_xkcd_raw_to_final = SparkSubmitOperator(
    task_id='pyspark_xkcd_raw_to_final',
    conn_id='spark',
    application='/home/airflow/airflow/python/xkcd_pyspark.py',
    total_executor_cores='2',
    executor_cores='2',
    executor_memory='2g',
    num_executors='2',
    name='xkcd_pyspark',
    verbose=True,
    dag = dag
)


create_local_import_dir_xkcd >> create_local_import_dir_raw >> create_local_init_file >> clear_local_import_dir >> download_xkcd >> hdfs_create_xkcd_dir >> hdfs_create_xkcd_raw_dir >> create_hdfs_init_file >> hdfs_clear_xkcd >> hdfs_push_xkcd >> pyspark_xkcd_raw_to_final

