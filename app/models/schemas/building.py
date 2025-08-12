from pydantic import BaseModel, ConfigDict


class BuildingRead(BaseModel):
    building_id: int
    address: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)
