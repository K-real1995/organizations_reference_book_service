from math import radians, sin, cos, sqrt, asin
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import EARTH_RADIUS
from app.models.building import Building
from app.models.organization import Organization


class OrganizationsRepository:

    @staticmethod
    def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        dlon = radians(lon2 - lon1)
        dlat = radians(lat2 - lat1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * asin(min(1.0, sqrt(a)))
        return EARTH_RADIUS * c

    @staticmethod
    async def list_all(session: AsyncSession) -> List[Organization]:
        stmt = select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        res = await session.execute(stmt)
        return res.scalars().unique().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, organization_id: int) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.organization_id == organization_id).options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        res = await session.execute(stmt)
        return res.scalars().unique().one_or_none()

    @staticmethod
    async def search_by_name(session: AsyncSession, name: str) -> List[Organization]:
        stmt = (
            select(Organization)
            .where(Organization.name.ilike(f"%{name}%"))
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().unique().all()

    @staticmethod
    async def get_organisations_in_building(session: AsyncSession, building_id: int) -> List[Organization]:
        stmt = (
            select(Organization)
            .where(Organization.building_id == building_id)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().unique().all()

    @staticmethod
    async def find_in_bbox(
            session: AsyncSession,
            lat_min: float,
            lon_min: float,
            lat_max: float,
            lon_max: float,
    ) -> List[Organization]:
        lat_lo, lat_hi = min(lat_min, lat_max), max(lat_min, lat_max)
        lon_lo, lon_hi = min(lon_min, lon_max), max(lon_min, lon_max)

        stmt = (
            select(Organization)
            .join(Building)
            .where(
                and_(
                    Building.latitude >= lat_lo,
                    Building.latitude <= lat_hi,
                    Building.longitude >= lon_lo,
                    Building.longitude <= lon_hi,
                )
            )
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
        )
        res = await session.execute(stmt)
        return res.scalars().unique().all()

    @staticmethod
    async def find_in_radius(session: AsyncSession, lat: float, lon: float, radius_km: float) -> List[Organization]:
        # BBOX предфильтр (чтобы не просматривать всю таблицу)
        deg_lat = radius_km / 110.574
        cos_lat = cos(radians(lat))
        deg_lon = radius_km / (111.320 * cos_lat) if abs(cos_lat) >= 1e-8 else 180.0

        lat_min, lat_max = lat - deg_lat, lat + deg_lat
        lon_min, lon_max = lon - deg_lon, lon + deg_lon

        b_stmt = select(Building.building_id, Building.latitude, Building.longitude).where(
            and_(
                Building.latitude.between(lat_min, lat_max),
                Building.longitude.between(lon_min, lon_max),
            )
        )
        b_res = await session.execute(b_stmt)
        rows = b_res.fetchall()

        building_ids: List[int] = []
        for row in rows:
            b_id, b_lat, b_lon = row
            if b_lat is None or b_lon is None:
                continue
            if OrganizationsRepository.haversine_km(lon, lat, b_lon, b_lat) <= radius_km:
                building_ids.append(b_id)

        if not building_ids:
            return []

        org_stmt = (
            select(Organization)
            .where(Organization.building_id.in_(building_ids))
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
        )
        org_res = await session.execute(org_stmt)
        return org_res.scalars().unique().all()
