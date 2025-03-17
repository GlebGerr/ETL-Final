# ETL-Final

Этот репозиторий содержит конвейер ETL, предназначенный для обработки, репликации и анализа данных. В рамках проекта данные генерируются, извлекаются из MongoDB и загружаются в PostgreSQL с использованием Apache Airflow.

## Используемые технологии

- **Apache Airflow** – автоматизация и управление задачами ETL.
- **MongoDB** – хранилище исходных данных, включающих пользовательские сессии, запросы, историю цен, обращения в поддержку и другие сущности.
- **PostgreSQL** – целевая база данных, в которой формируются аналитические витрины.
- **Docker** – контейнеризация для удобного развертывания и работы с сервисами.
- **Python** – основной язык программирования для ETL-процессов и генерации данных.

## Структура проекта

```plaintext
ETL-Final/
├── .env                        # Переменные окружения для сервисов
├── docker-compose.yml          # Конфигурация Docker Compose
├── README.md                   # Документация проекта
├── tasks.md                    # Описание задач и функций
├── .gitignore                  # Файлы, исключаемые из репозитория
│
├── airflow/                    # Директория с настройками и кодом Airflow
│   ├── Dockerfile              # Конфигурация образа Airflow
│   ├── requirements.txt        # Список зависимостей
│   ├── config/
│   │   └── airflow.cfg         # Конфигурационный файл
│   ├── dags/                   # DAG-файлы для Airflow
│   │   ├── sql/                # SQL-запросы для аналитических витрин
│   │   │   ├── support_efficiency.sql   # Витрина эффективности поддержки
│   │   │   └── users_activity.sql       # Витрина пользовательской активности
│   │   ├── etl_sessions.py     # DAG для user_sessions
│   │   ├── etl_logs.py         # DAG для event_logs
│   │   ├── etl_queries.py      # DAG для search_queries
│   │   ├── etl_recommendations.py # DAG для user_recommendations
│   │   ├── etl_moderation.py   # DAG для moderation_queue
│   │   ├── etl_tickets.py      # DAG для support_tickets
│   │   ├── etl_prices.py       # DAG для product_price_history
│   ├── logs/                   # Логи работы Airflow
│   └── plugins/                # Плагины Airflow  
│
├── data_generator/             # Сервис генерации тестовых данных
│   ├── Dockerfile              # Докерфайл генератора
│   ├── generate.py             # Скрипт генерации данных
│   └── requirements.txt        # Зависимости
│
└── db/                         # Базы данных проекта
    ├── mongo/                  # MongoDB
    └── postgres/               # PostgreSQL
```

## Развертывание

### 1. Клонирование репозитория

```bash
git clone https://github.com/GlebGerr/ETL-Final.git
cd ETL-Final
```

### 2. Настройка переменных окружения

Создайте `.env`-файл, используя шаблон `.env.example`, и заполните его параметрами:

```plaintext
MONGO_URI=mongodb://admin:admin@mongo:27017/
MONGO_DB=source_db
POSTGRES_HOST=postgres
POSTGRES_DB=etl_db
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpasswd
```

### 3. Запуск контейнеров

```bash
docker-compose up -d
```

### 4. Доступ к Airflow

Перейдите в браузере:

```
http://localhost:8080
```

### 5. Запуск DAG'ов

1. Открыть веб-интерфейс Apache Airflow.
2. Запустить DAG'и для репликации и аналитики.

## Генерация тестовых данных

Генератор автоматически создает и загружает в MongoDB тестовые данные.

Примеры данных:

- **user\_sessions** – информация о сессиях пользователей.
- **product\_price\_history** – история изменения цен.
- **event\_logs** – логи событий.
- **support\_tickets** – обращения в поддержку.
- **user\_recommendations** – рекомендации товаров.
- **moderation\_queue** – очередь модерации.
- **search\_queries** – поисковые запросы.

## Описание ETL-процессов

### Репликация данных

| DAG ID                | Источник данных                 | Назначение в PostgreSQL        |
| --------------------- | ------------------------------- | ------------------------------ |
| `etl_sessions`        | `MongoDB.user_sessions`         | `source.user_sessions`         |
| `etl_logs`            | `MongoDB.event_logs`            | `source.event_logs`            |
| `etl_queries`         | `MongoDB.search_queries`        | `source.search_queries`        |
| `etl_recommendations` | `MongoDB.user_recommendations`  | `source.user_recommendations`  |
| `etl_moderation`      | `MongoDB.moderation_queue`      | `source.moderation_queue`      |
| `etl_tickets`         | `MongoDB.support_tickets`       | `source.support_tickets`       |
| `etl_prices`          | `MongoDB.product_price_history` | `source.product_price_history` |

## Контакты

Автор: *Гераськин Глеб*\
Email: *[geraskin.gleb@gmail.com](mailto:geraskin.gleb@gmail.com)*

