from sqlalchemy import Table, Column, Integer, ForeignKey

from app.utils.db import Base

organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id",
        Integer,
        ForeignKey("organizations.organization_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "activity_type_id",
        Integer,
        ForeignKey("activity_types.activity_type_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)
