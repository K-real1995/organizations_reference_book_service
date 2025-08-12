from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building


class BuildingsRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, building_id: int) -> Optional[Building]:
        return await session.get(Building, building_id)
