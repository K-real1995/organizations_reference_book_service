from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.activity_hierarchy import build_activity_hierarchy
from app.core.constants import MAX_DEPTH_DEFAULT
from app.models.activity_type import ActivityType
from app.models.schemas.organization import OrganizationRead
from app.repositories.organizations_repository import OrganizationsRepository


class OrganizationsService:
    def __init__(self, organizations_repository: OrganizationsRepository = OrganizationsRepository()):
        self.organizations_repository = organizations_repository

    @staticmethod
    async def _load_activity_objects_by_ids(session, ids):

        stmt = select(ActivityType).where(ActivityType.activity_type_id.in_(list(ids) if ids else []))
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_all_organizations(self, session: AsyncSession, max_depth: int = MAX_DEPTH_DEFAULT) -> (
            List)[OrganizationRead]:
        orm_list = await self.organizations_repository.list_all(session)
        result = []
        for org in orm_list:
            assigned = getattr(org, "activities", None)
            activities_tree = await build_activity_hierarchy(session, list(assigned), max_depth=max_depth)

            bld = getattr(org, "building", None)
            building_payload = None
            if bld is not None:
                building_payload = {
                    "building_id": bld.building_id,
                    "address": bld.address,
                    "latitude": bld.latitude,
                    "longitude": bld.longitude,
                }

            phones_payload = []
            for p in getattr(org, "phones", []) or []:
                phones_payload.append({"phone_id": p.phone_id, "number": p.number})

            org_dict = {
                "organization_id": org.organization_id,
                "name": org.name,
                "building": building_payload,
                "phones": phones_payload,
                "activities": activities_tree,
            }

            result.append(OrganizationRead(**org_dict))
        return result

    async def get_organization_by_id(self, session: AsyncSession, organization_id: int,
                                     max_depth: int = MAX_DEPTH_DEFAULT) -> OrganizationRead:
        organization = await self.organizations_repository.get_by_id(session, organization_id)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        assigned = getattr(organization, "activities", None)
        activities_tree = await build_activity_hierarchy(session, list(assigned), max_depth=max_depth)

        building = getattr(organization, "building", None)
        building_payload = None
        if building is not None:
            building_payload = {
                "building_id": building.building_id,
                "address": building.address,
                "latitude": building.latitude,
                "longitude": building.longitude,
            }

        phones_payload = []
        for p in getattr(organization, "phones", []) or []:
            phones_payload.append({"phone_id": p.phone_id, "number": p.number})

        org_dict = {
            "organization_id": organization.organization_id,
            "name": organization.name,
            "building": building_payload,
            "phones": phones_payload,
            "activities": activities_tree,
        }

        return OrganizationRead(**org_dict)

    async def get_organization_by_name(self, session: AsyncSession, name: str, max_depth: int = MAX_DEPTH_DEFAULT) -> \
            List[OrganizationRead]:
        orm_list = await self.organizations_repository.search_by_name(session, name)
        out = []
        for org in orm_list:
            assigned = getattr(org, "activities", None)
            activities_tree = await build_activity_hierarchy(session, list(assigned), max_depth=max_depth)

            bld = getattr(org, "building", None)
            building_payload = None
            if bld is not None:
                building_payload = {
                    "building_id": bld.building_id,
                    "address": bld.address,
                    "latitude": bld.latitude,
                    "longitude": bld.longitude,
                }

            phones_payload = []
            for p in getattr(org, "phones", []) or []:
                phones_payload.append({"phone_id": p.phone_id, "number": p.number})

            org_dict = {
                "organization_id": org.organization_id,
                "name": org.name,
                "building": building_payload,
                "phones": phones_payload,
                "activities": activities_tree,
            }

            out.append(OrganizationRead(**org_dict))

        return out

    async def find_within_radius(self, session: AsyncSession, lat: float, lon: float, radius_km: float,
                                 max_depth: int = MAX_DEPTH_DEFAULT) -> List[OrganizationRead]:
        organizations_list = await self.organizations_repository.find_in_radius(session, lat, lon, radius_km)
        result = []
        for organization in organizations_list:
            assigned = getattr(organization, "activities", None)
            activities_tree = await build_activity_hierarchy(session, list(assigned), max_depth=max_depth)

            building = getattr(organization, "building", None)

            building_payload = None

            if building is not None:
                building_payload = {
                    "building_id": building.building_id,
                    "address": building.address,
                    "latitude": building.latitude,
                    "longitude": building.longitude,
                }

            phones_payload = []
            for p in getattr(organization, "phones", []) or []:
                phones_payload.append({"phone_id": p.phone_id, "number": p.number})

            org_dict = {
                "organization_id": organization.organization_id,
                "name": organization.name,
                "building": building_payload,
                "phones": phones_payload,
                "activities": activities_tree,
            }

            result.append(OrganizationRead(**org_dict))
        return result

    async def get_organizations_within(self, session: AsyncSession, lat_min: float, lon_min: float, lat_max: float,
                                       lon_max: float,
                                       max_depth: int = MAX_DEPTH_DEFAULT) -> List[OrganizationRead]:
        organizations_list = await self.organizations_repository.find_in_bbox(session, lat_min, lon_min, lat_max,
                                                                              lon_max)
        result = []
        for org in organizations_list:
            assigned = getattr(org, "activities", None)
            activities_tree = await build_activity_hierarchy(session, list(assigned), max_depth=max_depth)

            building = getattr(org, "building", None)

            building_payload = None

            if building is not None:
                building_payload = {
                    "building_id": building.building_id,
                    "address": building.address,
                    "latitude": building.latitude,
                    "longitude": building.longitude,
                }

            phones_payload = []
            for phones in getattr(org, "phones", []) or []:
                phones_payload.append({"phone_id": phones.phone_id, "number": phones.number})

            organization_dict = {
                "organization_id": org.organization_id,
                "name": org.name,
                "building": building_payload,
                "phones": phones_payload,
                "activities": activities_tree,
            }

            result.append(OrganizationRead(**organization_dict))

        return result
