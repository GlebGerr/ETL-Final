import os
import random
import uuid
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
from faker import Faker
from dotenv import load_dotenv

# �������� ���������� ���������
load_dotenv()

# ��������� �����������
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ������������ MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin@mongo:27017")
DB_NAME = os.getenv("MONGO_DB", "data_warehouse")

# ����������� � MongoDB
def get_mongo_connection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # �������� �����������
        return client[DB_NAME]
    except errors.ServerSelectionTimeoutError as e:
        logging.error(f"������ ����������� � MongoDB: {e}")
        exit(1)

# ������������� Faker
fake = Faker()

# ��������� ��������� ������
def generate_user_ids(count):
    return [str(uuid.uuid4()) for _ in range(count)]

def generate_product_ids(count):
    return [str(uuid.uuid4()) for _ in range(count)]

# ��������� ������ ��� ���������
def create_session_data(count, users):
    return [{
        "session_id": str(uuid.uuid4()),
        "user_id": random.choice(users),
        "start_time": (start_time := fake.date_time_this_year()).isoformat(),
        "end_time": (start_time + timedelta(minutes=random.randint(5, 120))).isoformat(),
        "pages_visited": [fake.uri_path() for _ in range(random.randint(1, 10))],
        "device": fake.user_agent(),
        "actions": [fake.word() for _ in range(random.randint(1, 5))]
    } for _ in range(count)]

def create_price_history_data(count, products):
    return [{
        "product_id": random.choice(products),
        "price_changes": [{
            "date": (datetime.now() - timedelta(days=i)).isoformat(),
            "price": round(random.uniform(10, 1000), 2)
        } for i in range(random.randint(1, 10))],
        "current_price": round(random.uniform(10, 1000), 2),
        "currency": "USD"
    } for _ in range(count)]

# ������� ������ � MongoDB
def save_data_to_mongodb(db, collection_name, data):
    try:
        db[collection_name].insert_many(data)
        logging.info(f"������ ��� {collection_name} ������� ���������: {len(data)} �������")
    except Exception as e:
        logging.error(f"������ ��� ���������� ������ � {collection_name}: {e}")

# �������� �������
def main():
    logging.info("?? ������ ��������� ������...")

    db = get_mongo_connection()
    users = generate_user_ids(int(os.getenv("USER_COUNT", 1000)))
    products = generate_product_ids(int(os.getenv("PRODUCT_COUNT", 500)))

    collections = {
        "user_sessions": (create_session_data, int(os.getenv("USER_SESSIONS_COUNT", 1000)), users),
        "product_price_history": (create_price_history_data, int(os.getenv("PRODUCT_PRICE_HISTORY_COUNT", 1000)), products)
    }

    for collection_name, (generator, count, *args) in collections.items():
        data = generator(count, *args)
        save_data_to_mongodb(db, collection_name, data)

    logging.info("? ��������� ������ ���������!")

if __name__ == "__main__":
    main()