-- ============================================
-- Схема базы данных маркетплейса
-- ============================================

-- Включаем расширение UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- TODO: Создать таблицу order_statuses
-- Столбцы: status (PK), description
CREATE TABLE IF NOT EXISTS order_statuses (
    status VARCHAR(20) PRIMARY KEY,
    description VARCHAR(100)
);

-- TODO: Вставить значения статусов
-- created, paid, cancelled, shipped, completed
INSERT INTO order_statuses (status, description) VALUES
    ('created', 'Заказ создан'),
    ('paid', 'Заказ оплачен'),
    ('cancelled', 'Заказ отменен'),
    ('shipped', 'Заказ отправлен'),
    ('completed', 'Заказ выполнен');

-- TODO: Создать таблицу users
-- Столбцы: id (UUID PK), email, name, created_at
-- Ограничения:
--   - email UNIQUE
--   - email NOT NULL и не пустой
--   - email валидный (regex через CHECK)
CREATE TABLE IF NOT EXISTS users
(
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE CHECK (
        email != '' AND email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    name VARCHAR(100) NOT NULL CHECK (name != ''),
    created_at TIMESTAMP WITH TIME ZONE,
);

-- TODO: Создать таблицу orders
-- Столбцы: id (UUID PK), user_id (FK), status (FK), total_amount, created_at
-- Ограничения:
--   - user_id -> users(id)
--   - status -> order_statuses(status)
--   - total_amount >= 0
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (status) REFERENCES order_statuses(status)
);

-- TODO: Создать таблицу order_items
-- Столбцы: id (UUID PK), order_id (FK), product_name, price, quantity
-- Ограничения:
--   - order_id -> orders(id) CASCADE
--   - price >= 0
--   - quantity > 0
--   - product_name не пустой
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    product_name VARCHAR(255) NOT NULL CHECK (product_name != ''),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),

    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- TODO: Создать таблицу order_status_history
-- Столбцы: id (UUID PK), order_id (FK), status (FK), changed_at
-- Ограничения:
--   - order_id -> orders(id) CASCADE
--   - status -> order_statuses(status)
CREATE TABLE IF NOT EXISTS order_status_history (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (status) REFERENCES order_statuses(status)
);

-- ============================================
-- КРИТИЧЕСКИЙ ИНВАРИАНТ: Нельзя оплатить заказ дважды
-- ============================================
-- TODO: Создать функцию триггера check_order_not_already_paid()
-- При изменении статуса на 'paid' проверить что его нет в истории
-- Если есть - RAISE EXCEPTION
CREATE OR REPLACE FUNCTION check_order_not_already_paid()
RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.status = 'paid' AND OLD.status IS DISTINCT FROM NEW.status THEN
        IF EXISTS (
            SELECT 1
            FROM order_status_history h
            WHERE h.order_id = NEW.id
              AND h.status = 'paid'
        ) THEN
            RAISE EXCEPTION 'Заказ % уже оплачен', NEW.id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TODO: Создать триггер trigger_check_order_not_already_paid
-- BEFORE UPDATE ON orders FOR EACH ROW
DROP TRIGGER IF EXISTS trigger_check_order_not_already_paid ON orders;

CREATE TRIGGER trigger_check_order_not_already_paid
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION check_order_not_already_paid();

-- ============================================
-- БОНУС (опционально)
-- ============================================
-- TODO: Триггер автоматического пересчета total_amount
-- TODO: Триггер автоматической записи в историю при изменении статуса
-- TODO: Триггер записи начального статуса при создании заказа
