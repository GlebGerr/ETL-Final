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
COLLECTION_NAME = "product_price_history"

# Название DAG
DAG_NAME = "etl_product_price_history"

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
    description="ETL для истории цен на товары"
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

    # Разворачиваем историю цен в отдельные строки
    df_exploded = df.explode("price_changes").reset_index(drop=True)

    # Нормализуем словари в price_changes
    price_history_df = df_exploded["price_changes"].apply(pd.Series)

    # Объединяем с исходными данными
    df_transformed = pd.concat([df_exploded.drop(columns=["price_changes"]), price_history_df], axis=1)

    # Удаляем дубликаты
    df_transformed.drop_duplicates(subset=['product_id', 'date'], inplace=True)
    df_transformed.dropna(axis="rows", how='any', inplace=True)

    logging.info(f"Трансформировано {len(df_transformed)} записей")
    ti.xcom_push(key='transformed_data', value=df_transformed.to_dict(orient='records'))

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
    df['date'] = pd.to_datetime(df['date'])

    # Меняем порядок столбцов
    neworder = ['product_id', 'date', 'price', 'currency', 'current_price']
    df = df.reindex(columns=neworder)

    # Устанавливаем индекс
    df.set_index(['product_id', 'date'], inplace=True)

    # Загружаем данные в PostgreSQL с обработкой дубликатов
    df.to_sql(COLLECTION_NAME, schema="source", con=engine, if_exists="append", index=True)

    logging.info(f"Загружено {len(df)} записей в PostgreSQL")

# Задачи DAG
task_start = DummyOperator(task_id='start', dag=dag)
task_extract = PythonOperator(task_id='extract', python_callable=extract, provide_context=True, dag=dag)
task_transform = PythonOperator(task_id='transform', python_callable=transform, provide_context=True, dag=dag)
task_load = PythonOperator(task_id='load', python_callable=load, provide_context=True, dag=dag)
task_finish = DummyOperator(task_id='finish', dag=dag)

# Определение порядка выполнения задач
task_start >> task_extract >> task_transform >> task_load >> task_finish