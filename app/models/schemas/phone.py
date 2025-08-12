from pydantic import BaseModel, ConfigDict


class PhoneRead(BaseModel):
    phone_id: int
    number: str

    model_config = ConfigDict(from_attributes=True)
