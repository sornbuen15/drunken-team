import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
import sqlalchemy.dialects.postgresql as pg
from .base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    devices = relationship(
        "Device", back_populates="customer", cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "SubscriptionService", back_populates="customer", cascade="all, delete-orphan"
    )
