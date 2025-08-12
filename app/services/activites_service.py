from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MAX_DEPTH_DEFAULT
from app.repositories.activities_repository import ActivitiesRepository
from app.core.activity_hierarchy import build_activity_hierarchy


class ActivitiesService:
    def __init__(self, activities_repository: ActivitiesRepository = ActivitiesRepository()):
        self.activities_repository = activities_repository

    async def get_organizations_by_activity_id(self, session: AsyncSession, activity_id: int,
                                               max_depth: int = MAX_DEPTH_DEFAULT):
        root = await self.activities_repository.get_activity(session, activity_id)
        if not root:
            raise HTTPException(status_code=404, detail="Activity type not found")

        subtype_ids = await self.activities_repository.get_subtype_ids_bfs(session, activity_id)
        organizations = await self.activities_repository.get_organizations_by_activity_ids(session, subtype_ids)

        results = []
        for organization in organizations:
            tree = await build_activity_hierarchy(session, organization.activities, max_depth=max_depth)
            results.append({
                "organization_id": organization.organization_id,
                "name": organization.name,
                "building": None if not organization.building else {
                    "building_id": organization.building.building_id,
                    "address": organization.building.address,
                    "latitude": organization.building.latitude,
                    "longitude": organization.building.longitude
                },
                "phones": [{"phone_id": p.phone_id, "number": p.number} for p in organization.phones or []],
                "activities": tree
            })
        return results
