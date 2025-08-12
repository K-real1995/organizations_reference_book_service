from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.db import Base


class Building(Base):
    __tablename__ = "buildings"

    building_id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)

    organizations: Mapped[list["Organization"]] = relationship(back_populates="building")
