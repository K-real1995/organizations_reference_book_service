from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.organization import OrganizationRead
from app.services.organizations_service import OrganizationsService
from app.utils.db import get_session
from app.utils.security import get_api_key

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(get_api_key)]
)

_organizations_service = OrganizationsService()


@router.get("/", response_model=List[OrganizationRead])
async def get_all_organizations(
        session: AsyncSession = Depends(get_session)
):
    return await _organizations_service.get_all_organizations(session)


@router.get("/search", response_model=List[OrganizationRead])
async def get_organizations_by_name(
        name: str = Query(..., min_length=1),
        session: AsyncSession = Depends(get_session)
):
    return await _organizations_service.get_organization_by_name(session, name)


@router.get("/near", response_model=List[OrganizationRead])
async def get_organizations_near(
        lat: float = Query(..., ge=-90.0, le=90.0),
        lon: float = Query(..., ge=-180.0, le=180.0),
        radius_km: float = Query(..., gt=0.0),
        session: AsyncSession = Depends(get_session)
):
    return await _organizations_service.find_within_radius(session, lat, lon, radius_km)


@router.get("/within", response_model=List[OrganizationRead])
async def get_organizations_within(
        lat_min: float = Query(...),
        lon_min: float = Query(...),
        lat_max: float = Query(...),
        lon_max: float = Query(...),
        session: AsyncSession = Depends(get_session)
):
    return await _organizations_service.get_organizations_within(session, lat_min, lon_min, lat_max, lon_max)


@router.get("/{organization_id}", response_model=OrganizationRead)
async def get_organization_by_id(
        organization_id: int,
        session: AsyncSession = Depends(get_session)
):
    return await _organizations_service.get_organization_by_id(session, organization_id)
