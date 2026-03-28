"""Реализация репозиториев с использованием SQLAlchemy."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import User
from app.domain.order import Order, OrderItem, OrderStatus, OrderStatusChange


class UserRepository:
    """Репозиторий для User."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # TODO: Реализовать save(user: User) -> None
    # Используйте INSERT ... ON CONFLICT DO UPDATE
    async def save(self, user: User) -> None:
        query = text(
            """
            INSERT INTO users (id, email, name, created_at)
            VALUES (:id, :email, :name, :created_at)
            ON CONFLICT (id) DO UPDATE
            SET
            email = EXCLUDED.email,
            name = EXCLUDED.name,
            created_at = EXCLUDED.created_at
            """
        )

        await self.session.execute(
            query,
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at,
            },
        )
    
    # TODO: Реализовать find_by_id(user_id: UUID) -> Optional[User]
    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        query = text(
            """
            SELECT id, email, name, created_at
            FROM users
            WHERE id = :user_id
            """
        )

        result = await self.session.execute(query, {"user_id": user_id})
        row = result.mappings().first()

        if row is None:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            created_at=row["created_at"],
        )

    # TODO: Реализовать find_by_email(email: str) -> Optional[User]
    async def find_by_email(self, email: str) -> Optional[User]:
        query = text(
            """
            SELECT id, email, name, created_at
            FROM users
            WHERE email = :email
            """
        )

        result = await self.session.execute(query, {"email": email})
        row = result.mappings().first()

        if row is None:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            created_at=row["created_at"],
        )

    # TODO: Реализовать find_all() -> List[User]
    async def find_all(self) -> List[User]:
        query = text(
            """
            SELECT id, email, name, created_at
            FROM users
            ORDER BY created_at
            """
        )

        result = await self.session.execute(query)
        rows = result.mappings().all()

        users = []
        for row in rows:
            users.append(
                User(
                    id=row["id"],
                    email=row["email"],
                    name=row["name"],
                    created_at=row["created_at"],
                )
            )

        return users


class OrderRepository:
    """Репозиторий для Order."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # TODO: Реализовать save(order: Order) -> None
    # Сохранить заказ, товары и историю статусов
    async def save(self, order: Order) -> None:
        order_query = text(
            """
            INSERT INTO orders (id, user_id, status, total_amount, created_at)
            VALUES (:id, :user_id, :status, :total_amount, :created_at)
            ON CONFLICT (id) DO UPDATE
            SET
                user_id = EXCLUDED.user_id,
                status = EXCLUDED.status,
                total_amount = EXCLUDED.total_amount
            """
        )

        await self.session.execute(
            order_query,
            {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status.value,
                "total_amount": order.total_amount,
                "created_at": order.created_at,
            },
        )

        delete_items_query = text(
            """
            DELETE FROM order_items
            WHERE order_id = :order_id
            """
        )
        await self.session.execute(delete_items_query, {"order_id": order.id})

        for item in order.items:
            item_query = text(
                """
                INSERT INTO order_items (id, order_id, product_name, price, quantity)
                VALUES (:id, :order_id, :product_name, :price, :quantity)
                """
            )

            await self.session.execute(
                item_query,
                {
                    "id": item.id,
                    "order_id": order.id,
                    "product_name": item.product_name,
                    "price": item.price,
                    "quantity": item.quantity,
                },
            )

        existing_history_query = text(
            """
            SELECT status, changed_at
            FROM order_status_history
            WHERE order_id = :order_id
            """
        )

        existing_result = await self.session.execute(
            existing_history_query, {"order_id": order.id}
        )
        existing_rows = existing_result.mappings().all()

        existing_set = {
            (row["status"], row["changed_at"]) for row in existing_rows
        }

        for status_change in order.status_history:
            key = (status_change.status.value, status_change.changed_at)

            if key not in existing_set:
                history_query = text(
                    """
                    INSERT INTO order_status_history (id, order_id, status, changed_at)
                    VALUES (:id, :order_id, :status, :changed_at)
                    """
                )

                await self.session.execute(
                    history_query,
                    {
                        "id": status_change.id,
                        "order_id": order.id,
                        "status": status_change.status.value,
                        "changed_at": status_change.changed_at,
                    },
                )

    # TODO: Реализовать find_by_id(order_id: UUID) -> Optional[Order]
    # Загрузить заказ со всеми товарами и историей
    # Используйте object.__new__(Order) чтобы избежать __post_init__
    async def find_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        order_query = text(
            """
            SELECT id, user_id, status, total_amount, created_at
            FROM orders
            WHERE id = :order_id
            """
        )

        result = await self.session.execute(order_query, {"order_id": order_id})
        row = result.mappings().first()

        if row is None:
            return None

        items_query = text(
            """
            SELECT id, order_id, product_name, price, quantity
            FROM order_items
            WHERE order_id = :order_id
            ORDER BY id
            """
        )
        items_result = await self.session.execute(items_query, {"order_id": order_id})
        item_rows = items_result.mappings().all()

        history_query = text(
            """
            SELECT id, order_id, status, changed_at
            FROM order_status_history
            WHERE order_id = :order_id
            ORDER BY changed_at
            """
        )
        history_result = await self.session.execute(history_query, {"order_id": order_id})
        history_rows = history_result.mappings().all()

        order = object.__new__(Order)
        order.user_id = row["user_id"]
        order.id = row["id"]
        order.status = OrderStatus(row["status"])
        order.total_amount = row["total_amount"]
        order.created_at = row["created_at"]
        order.items = []
        order.status_history = []

        for item_row in item_rows:
            item = object.__new__(OrderItem)
            item.product_name = item_row["product_name"]
            item.price = item_row["price"]
            item.quantity = item_row["quantity"]
            item.id = item_row["id"]
            item.order_id = item_row["order_id"]
            order.items.append(item)

        for history_row in history_rows:
            status_change = object.__new__(OrderStatusChange)
            status_change.order_id = history_row["order_id"]
            status_change.status = OrderStatus(history_row["status"])
            status_change.changed_at = history_row["changed_at"]
            status_change.id = history_row["id"]
            order.status_history.append(status_change)

        return order

    # TODO: Реализовать find_by_user(user_id: UUID) -> List[Order]
    async def find_by_user(self, user_id: uuid.UUID) -> List[Order]:
        query = text(
            """
            SELECT id
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at
            """
        )

        result = await self.session.execute(query, {"user_id": user_id})
        rows = result.mappings().all()

        orders = []
        for row in rows:
            order = await self.find_by_id(row["id"])
            if order is not None:
                orders.append(order)

        return orders

    # TODO: Реализовать find_all() -> List[Order]
    async def find_all(self) -> List[Order]:
        query = text(
            """
            SELECT id
            FROM orders
            ORDER BY created_at
            """
        )

        result = await self.session.execute(query)
        rows = result.mappings().all()

        orders = []
        for row in rows:
            order = await self.find_by_id(row["id"])
            if order is not None:
                orders.append(order)

        return orders
