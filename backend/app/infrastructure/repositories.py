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
        raise NotImplementedError("TODO: Реализовать OrderRepository.save")

    # TODO: Реализовать find_by_id(order_id: UUID) -> Optional[Order]
    # Загрузить заказ со всеми товарами и историей
    # Используйте object.__new__(Order) чтобы избежать __post_init__
    async def find_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        raise NotImplementedError("TODO: Реализовать OrderRepository.find_by_id")

    # TODO: Реализовать find_by_user(user_id: UUID) -> List[Order]
    async def find_by_user(self, user_id: uuid.UUID) -> List[Order]:
        raise NotImplementedError("TODO: Реализовать OrderRepository.find_by_user")

    # TODO: Реализовать find_all() -> List[Order]
    async def find_all(self) -> List[Order]:
        raise NotImplementedError("TODO: Реализовать OrderRepository.find_all")
