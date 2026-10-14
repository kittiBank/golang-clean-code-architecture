from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.domain.repositories import CrudRepository


class SqlAlchemyCrudRepository(CrudRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, model: type[Base], record_id: int) -> Base | None:
        return self.db.get(model, record_id)

    def list(
        self, model: type[Base], *, offset: int, limit: int, filters: dict[str, Any]
    ) -> tuple[Sequence[Base], int]:
        conditions = [getattr(model, field) == value for field, value in filters.items()]

        total = self.db.scalar(select(func.count()).select_from(model).where(*conditions))
        records = self.db.scalars(
            select(model).where(*conditions).order_by(model.id).offset(offset).limit(limit)
        ).all()
        return records, total or 0
