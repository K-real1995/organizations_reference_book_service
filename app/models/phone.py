from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.db import Base


class Phone(Base):
    __tablename__ = "phones"

    phone_id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(nullable=False)

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.organization_id", ondelete="CASCADE"))
    organization: Mapped["Organization"] = relationship(back_populates="phones")
