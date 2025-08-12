from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    organization_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.building_id"), nullable=False)
    building: Mapped["Building"] = relationship(back_populates="organizations")

    phones: Mapped[List["Phone"]] = relationship(back_populates="organization", cascade="all, delete-orphan")

    activities: Mapped[List["ActivityType"]] = relationship(
        "ActivityType",
        secondary="organization_activity",
        back_populates="organizations"
    )
