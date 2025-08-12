from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.organization import OrganizationRead
from app.services.buildings_service import BuildingsService
from app.utils.db import get_session

router = APIRouter(prefix="/buildings", tags=["Buildings"])

_building_service = BuildingsService()


@router.get("/{building_id}/organizations", response_model=List[OrganizationRead])
async def orgs_in_building(
        building_id: int,
        session: AsyncSession = Depends(get_session)
):
    return await _building_service.get_organizations_in_building(session, building_id)
