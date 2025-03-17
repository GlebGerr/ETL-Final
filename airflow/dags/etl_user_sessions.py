import logging
import os
from datetime import datetime
import pandas as pd

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Логирование
logging.basicConfig(level=logging.INFO)

# Название коллекции MongoDB
COLLECTION_NAME = "user_sessions"

# Название DAG
DAG_NAME = "etl_user_sessions"

# Аргументы по умолчанию для DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 17),
    'retries': 1,
}

# Создание DAG
dag = DAG(
    DAG_NAME,
    default_args=default_args,
    schedule_interval=None,
    is_paused_upon_creation=False,
    catchup=False,
    description="ETL для сессий пользователей"
)

def extract(**kwargs):
    """Извлекает данные из MongoDB."""
    mongo_hook = MongoHook(mongo_conn_id='etl_mongo')
    client = mongo_hook.get_conn()
    db_name = os.getenv("MONGO_DB", "source_db")
    collection = client[db_name][COLLECTION_NAME]

    extracted_data = list(collection.find({}, {"_id": 0}))
    logging.info(f"Извлечено {len(extracted_data)} записей")

    kwargs['ti'].xcom_push(key='extracted_data', value=extracted_data)

def transform(**kwargs):
    """Обрабатывает данные перед загрузкой в PostgreSQL."""
    ti = kwargs['ti']
    extracted_data = ti.xcom_pull(task_ids='extract', key='extracted_data')

    if not extracted_data:
        logging.warning("Нет данных для трансформации")
        return

    df = pd.DataFrame(extracted_data)

    # Заполняем NaN в списках пустыми значениями
    df['pages_visited'] = df['pages_visited'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
    df['actions'] = df['actions'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')

    # Удаляем дубликаты
    df.drop_duplicates(subset=["session_id"], inplace=True)
    df.fillna("", inplace=True)

    logging.info(f"Трансформировано {len(df)} записей")
    ti.xcom_push(key='transformed_data', value=df.to_dict(orient='records'))

def load(**kwargs):
    """Загружает данные в PostgreSQL."""
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform', key='transformed_data')

    if not transformed_data:
        logging.warning("Нет данных для загрузки")
        return

    pg_hook = PostgresHook(postgres_conn_id="etl_postgres")
    engine = pg_hook.get_sqlalchemy_engine()

    df = pd.DataFrame(transformed_data)

    # Преобразуем поля в datetime
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    # Устанавливаем индекс
    df.set_index("session_id", inplace=True)

    # Загружаем данные в PostgreSQL
    df.to_sql(COLLECTION_NAME, schema="source", con=engine, if_exists="replace", index=True)

    logging.info(f"Загружено {len(df)} записей в PostgreSQL")

# Задачи DAG
task_start = DummyOperator(task_id='start', dag=dag)
task_extract = PythonOperator(task_id='extract', python_callable=extract, provide_context=True, dag=dag)
task_transform = PythonOperator(task_id='transform', python_callable=transform, provide_context=True, dag=dag)
task_load = PythonOperator(task_id='load', python_callable=load, provide_context=True, dag=dag)
task_finish = DummyOperator(task_id='finish', dag=dag)

# Определение порядка выполнения задач
task_start >> task_extract >> task_transform >> task_load >> task_finish