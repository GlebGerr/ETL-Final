-- Удаление таблицы, если она существует
DROP TABLE IF EXISTS mart.support_efficiency_mart;

-- Создание витрины эффективности поддержки
CREATE TABLE mart.support_efficiency_mart AS
WITH ticket_data AS (
    SELECT
        DATE(created_at) AS created_date,                     -- Дата создания тикета
        TO_CHAR(created_at, 'YYYY-MM') AS created_month,      -- Месяц создания тикета
        issue_type,                                           -- Тип проблемы
        COUNT(ticket_id) AS total_tickets,                    -- Общее количество тикетов
        COUNT(*) FILTER (WHERE status = 'open') AS open_tickets,       -- Количество открытых тикетов
        COUNT(*) FILTER (WHERE status = 'pending') AS pending_tickets, -- Количество тикетов в ожидании
        COUNT(*) FILTER (WHERE status = 'closed') AS closed_tickets,   -- Количество закрытых тикетов
        ROUND(
            AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 60)   -- Среднее время решения в минутах
            FILTER (WHERE status = 'closed'), 2
        ) AS avg_resolution_time_minutes
    FROM source.support_tickets
    GROUP BY DATE(created_at), TO_CHAR(created_at, 'YYYY-MM'), issue_type
)
SELECT
    created_date,                                             -- Дата создания
    created_month,                                            -- Месяц создания
    issue_type,                                               -- Тип проблемы
    total_tickets,                                            -- Общее количество тикетов
    open_tickets,                                             -- Открытые тикеты
    pending_tickets,                                          -- Тикеты в ожидании
    closed_tickets,                                           -- Закрытые тикеты
    avg_resolution_time_minutes,                              -- Среднее время решения
    SUM(total_tickets) OVER(PARTITION BY created_month, issue_type) AS monthly_total_tickets,    -- Всего тикетов за месяц
    SUM(open_tickets) OVER(PARTITION BY created_month, issue_type) AS monthly_open_tickets,      -- Открытых тикетов за месяц
    SUM(pending_tickets) OVER(PARTITION BY created_month, issue_type) AS monthly_pending_tickets, -- Тикетов в ожидании за месяц
    SUM(closed_tickets) OVER(PARTITION BY created_month, issue_type) AS monthly_closed_tickets   -- Закрытых тикетов за месяц
FROM ticket_data
ORDER BY created_date;

-- Создание индексов для ускорения поиска
CREATE INDEX idx_support_efficiency_created_date ON mart.support_efficiency_mart (created_date);
CREATE INDEX idx_support_efficiency_created_month ON mart.support_efficiency_mart (created_month);
CREATE INDEX idx_support_efficiency_issue_type ON mart.support_efficiency_mart (issue_type);