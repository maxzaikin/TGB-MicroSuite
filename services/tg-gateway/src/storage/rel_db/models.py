"""tgrambuddy/src/aio_api/database/models.py"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_adapter import Model


class Client(Model):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    t_id: Mapped[int] = mapped_column(Integer, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    photos: Mapped[list["Photo"]] = relationship(
        cascade="all, delete-orphan", back_populates="client"
    )

    def __repr__(self):
        return f'Client({self.id}, {self.t_id}, "{self.name}")'
