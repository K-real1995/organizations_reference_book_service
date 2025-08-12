from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity_type import ActivityType
from app.models.organization import Organization


class ActivitiesRepository:
    @staticmethod
    async def get_activity(session: AsyncSession, activity_id: int) -> ActivityType | None:
        return await session.get(ActivityType, activity_id)

    @staticmethod
    async def get_subtype_ids_bfs(session: AsyncSession, root_id: int) -> List[int]:
        ids = [root_id]
        queue = [root_id]
        while queue:
            pid = queue.pop()
            stmt = select(ActivityType.activity_type_id).where(ActivityType.parent_id == pid)
            res = await session.execute(stmt)
            children_ids = [row[0] for row in res.fetchall()]
            for cid in children_ids:
                if cid not in ids:
                    ids.append(cid)
                    queue.append(cid)
        return ids

    @staticmethod
    async def get_organizations_by_activity_ids(session: AsyncSession, activity_ids: List[int]):
        stmt = (
            select(Organization)
            .join(Organization.activities)
            .where(ActivityType.activity_type_id.in_(activity_ids))
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
            .distinct()
        )
        res = await session.execute(stmt)
        return res.scalars().all()
