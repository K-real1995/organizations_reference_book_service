from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.activity_hierarchy import build_activity_hierarchy
from app.core.constants import MAX_DEPTH_DEFAULT
from app.models.organization import Organization
from app.models.schemas.organization import OrganizationRead
from app.repositories.activities_repository import ActivitiesRepository
from app.repositories.buildings_repository import BuildingsRepository
from app.repositories.organizations_repository import OrganizationsRepository


class BuildingsService:
    def __init__(
            self,
            building_repository: BuildingsRepository = BuildingsRepository(),
            organizations_repository: OrganizationsRepository = OrganizationsRepository(),
            activities_repository: ActivitiesRepository = ActivitiesRepository()
    ):
        self.building_repository = building_repository
        self.organizations_repository = organizations_repository
        self.activities_repository = activities_repository

    async def get_organizations_in_building(
            self,
            session: AsyncSession,
            building_id: int,
            max_depth: int = MAX_DEPTH_DEFAULT
    ) -> List[OrganizationRead]:
        building = await self.building_repository.get_by_id(session, building_id)
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")

        organizations: List[Organization] = await self.organizations_repository.get_organisations_in_building(
            session, building_id
        )

        result: List[OrganizationRead] = []
        for organization in organizations:
            assigned = getattr(organization, "activities", None)
            activities_tree = await build_activity_hierarchy(session, list(assigned), max_depth=max_depth)

            bld = getattr(organization, "building", None)
            building_payload = None
            if bld is not None:
                building_payload = {
                    "building_id": bld.building_id,
                    "address": bld.address,
                    "latitude": bld.latitude,
                    "longitude": bld.longitude,
                }

            phones_payload = []
            for phone in getattr(organization, "phones", []) or []:
                phones_payload.append({"phone_id": phone.phone_id, "number": phone.number})

            org_dict = {
                "organization_id": organization.organization_id,
                "name": organization.name,
                "building": building_payload,
                "phones": phones_payload,
                "activities": activities_tree,
            }

            result.append(OrganizationRead(**org_dict))

        return result
