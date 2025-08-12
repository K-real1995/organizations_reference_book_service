from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.organization_activity import organization_activity
from app.utils.db import Base


class ActivityType(Base):
    __tablename__ = "activity_types"

    activity_type_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("activity_types.activity_type_id"), nullable=True)

    parent: Mapped["ActivityType"] = relationship(
        "ActivityType", remote_side=[activity_type_id], backref="children"
    )

    organizations: Mapped[List["Organization"]] = relationship(
        "Organization",
        secondary=organization_activity,
        back_populates="activities"
    )
