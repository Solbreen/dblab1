-- ============================================
-- Схема базы данных маркетплейса
-- ============================================

-- Включаем расширение UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- TODO: Создать таблицу order_statuses
-- Столбцы: status (PK), description
CREATE TABLE IF NOT EXISTS order_statuses (
    status VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL
);

-- TODO: Вставить значения статусов
-- created, paid, cancelled, shipped, completed
INSERT INTO order_statuses (status, description) VALUES
    ('created', 'Заказ создан, ожидает оплаты'),
    ('paid', 'Заказ оплачен'),
    ('cancelled', 'Заказ отменен'),
    ('shipped', 'Заказ отправлен'),
    ('completed', 'Заказ выполнен')
ON CONFLICT (status) DO NOTHING;

-- TODO: Создать таблицу users
-- Столбцы: id (UUID PK), email, name, created_at
-- Ограничения:
--   - email UNIQUE
--   - email NOT NULL и не пустой
--   - email валидный (regex через CHECK)
CREATE TABLE IF NOT EXISTS users
(
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE CHECK (email != ''),
    name VARCHAR(100) NOT NULL CHECK (name != ''),
    created_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT email_not_empty CHECK (email != '')
);

-- TODO: Создать таблицу orders
-- Столбцы: id (UUID PK), user_id (FK), status (FK), total_amount, created_at
-- Ограничения:
--   - user_id -> users(id)
--   - status -> order_statuses(status)
--   - total_amount >= 0
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешние ключи
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE RESTRICT,
    
    CONSTRAINT fk_orders_status FOREIGN KEY (status) 
        REFERENCES order_statuses(status),
    
    -- Сумма заказа не может быть отрицательной
    CONSTRAINT total_amount_non_negative CHECK (total_amount >= 0)
);

-- TODO: Создать таблицу order_items
-- Столбцы: id (UUID PK), order_id (FK), product_name, price, quantity
-- Ограничения:
--   - order_id -> orders(id) CASCADE
--   - price >= 0
--   - quantity > 0
--   - product_name не пустой
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    
    -- Внешний ключ с каскадным удалением
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) 
        REFERENCES orders(id) ON DELETE CASCADE,
    
    -- Цена не может быть отрицательной
    CONSTRAINT price_non_negative CHECK (price >= 0),
    
    -- Количество должно быть положительным
    CONSTRAINT quantity_positive CHECK (quantity > 0),
    
    -- Название товара не должно быть пустым
    CONSTRAINT product_name_not_empty CHECK (product_name != '')
);

-- TODO: Создать таблицу order_status_history
-- Столбцы: id (UUID PK), order_id (FK), status (FK), changed_at
-- Ограничения:
--   - order_id -> orders(id) CASCADE
--   - status -> order_statuses(status)
CREATE TABLE IF NOT EXISTS order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешние ключи с каскадным удалением
    CONSTRAINT fk_history_order FOREIGN KEY (order_id) 
        REFERENCES orders(id) ON DELETE CASCADE,
    
    CONSTRAINT fk_history_status FOREIGN KEY (status) 
        REFERENCES order_statuses(status)
);

-- ============================================
-- КРИТИЧЕСКИЙ ИНВАРИАНТ: Нельзя оплатить заказ дважды
-- ============================================
-- TODO: Создать функцию триггера check_order_not_already_paid()
-- При изменении статуса на 'paid' проверить что его нет в истории
-- Если есть - RAISE EXCEPTION


-- TODO: Создать триггер trigger_check_order_not_already_paid
-- BEFORE UPDATE ON orders FOR EACH ROW


-- ============================================
-- БОНУС (опционально)
-- ============================================
-- TODO: Триггер автоматического пересчета total_amount
-- TODO: Триггер автоматической записи в историю при изменении статуса
-- TODO: Триггер записи начального статуса при создании заказа
