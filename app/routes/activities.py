from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.activites_service import ActivitiesService
from app.utils.db import get_session
from app.utils.security import get_api_key

router = APIRouter(prefix="/activities", tags=["Activities"], dependencies=[Security(get_api_key)])

_activities_service = ActivitiesService()


@router.get("/{activity_id}/organizations")
async def get_organizations_by_activity_id(activity_id: int, session: AsyncSession = Depends(get_session)):
    return await _activities_service.get_organizations_by_activity_id(session, activity_id)
