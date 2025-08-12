from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.schemas.activity_type import ActivityTypeRead
from app.models.schemas.building import BuildingRead
from app.models.schemas.phone import PhoneRead


class OrganizationRead(BaseModel):
    organization_id: int
    name: str
    building: BuildingRead
    phones: List[PhoneRead] = Field(default_factory=list)
    activities: List[ActivityTypeRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
