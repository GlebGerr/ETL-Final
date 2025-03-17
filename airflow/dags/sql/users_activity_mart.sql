-- Удаление таблицы, если она существует
DROP TABLE IF EXISTS mart.user_activity_mart;

-- Создание витрины пользовательской активности
CREATE TABLE mart.user_activity_mart AS
SELECT
    s.user_id,                                                -- Идентификатор пользователя
    COUNT(s.session_id) AS total_sessions,                    -- Общее количество сессий
    TO_CHAR(MIN(s.start_time), 'DD-MM-YYYY HH24:MI') AS first_session_start_time,  -- Время первой сессии
    TO_CHAR(MAX(s.end_time), 'DD-MM-YYYY HH24:MI') AS last_session_end_time,       -- Время последней сессии
    ROUND(AVG(EXTRACT(EPOCH FROM (s.end_time - s.start_time)) / 60), 2) AS avg_session_duration_minutes,  -- Средняя продолжительность сессии
    ROUND(SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time)) / 60), 2) AS total_session_duration_minutes, -- Общая продолжительность сессий
    COUNT(DISTINCT q.query_id) AS search_queries_count,       -- Количество поисковых запросов
    COUNT(DISTINCT t.ticket_id) AS support_tickets_count,     -- Количество обращений в поддержку
    COUNT(DISTINCT ur.recommended_product) AS recommended_products_count  -- Количество рекомендованных товаров
FROM source.user_sessions s
LEFT JOIN source.search_queries q ON s.user_id = q.user_id    -- Поисковые запросы пользователя
LEFT JOIN source.support_tickets t ON s.user_id = t.user_id   -- Обращения в поддержку
LEFT JOIN source.user_recommendations ur ON s.user_id = ur.user_id  -- Рекомендации товаров
GROUP BY s.user_id;

-- Создание индекса для ускорения поиска по user_id
CREATE INDEX idx_user_activity_mart_user_id ON mart.user_activity_mart (user_id);