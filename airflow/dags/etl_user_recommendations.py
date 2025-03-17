import logging
import os
import pandas as pd
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Логирование
logging.basicConfig(level=logging.INFO)

# Название коллекции MongoDB
COLLECTION_NAME = "user_recommendations"

# Название DAG
DAG_NAME = "etl_user_recommendations"

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
    description="ETL для рекомендаций пользователям"
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

    # Разворачиваем рекомендованные продукты в отдельные строки
    df_exploded = df.explode("recommended_products").reset_index(drop=True)
    df_exploded = df_exploded.rename(columns={'recommended_products': 'recommended_product'})

    # Удаляем дубликаты
    df_exploded.drop_duplicates(subset=['user_id', 'recommended_product'], inplace=True)
    df_exploded.dropna(axis="rows", how='any', inplace=True)

    logging.info(f"Трансформировано {len(df_exploded)} записей")
    ti.xcom_push(key='transformed_data', value=df_exploded.to_dict(orient='records'))

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

    # Преобразуем поля