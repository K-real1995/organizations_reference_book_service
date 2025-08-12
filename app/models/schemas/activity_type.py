from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class ActivityTypeRead(BaseModel):
    activity_type_id: int
    name: str
    parent_id: Optional[int] = None

    children: List["ActivityTypeRead"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
