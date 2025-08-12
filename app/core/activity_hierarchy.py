from typing import Iterable, List, Set, Union, Optional, Dict

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MAX_DEPTH_DEFAULT
from app.models.activity_type import ActivityType


# Функция постройки дерева активностей
async def build_activity_hierarchy(
        session: AsyncSession,
        activities_or_ids: Iterable[Union[ActivityType, int]],
        max_depth: int = MAX_DEPTH_DEFAULT,
) -> List[Dict]:
    # нормализуем вход в set of ids
    start_ids: Set[int] = set()
    for it in activities_or_ids or []:
        if isinstance(it, ActivityType):
            start_ids.add(int(it.activity_type_id))
        else:
            start_ids.add(int(it))

    if not start_ids:
        return []

    # 1) поднимаемся вверх от start_ids собирая родителей до max_depth
    all_ids: Set[int] = set(start_ids)
    current_level: Set[int] = set(start_ids)
    depth = 0
    child_to_parent: Dict[int, Optional[int]] = {}

    while current_level:
        if depth >= max_depth:
            # проверяем, есть ли ещё родители вне all_ids — тогда превышаем лимит
            stmt = select(ActivityType.parent_id).where(ActivityType.activity_type_id.in_(list(all_ids)))
            res = await session.execute(stmt)
            parents = [r[0] for r in res.fetchall() if r[0] is not None]
            if any(p not in all_ids for p in parents):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Activity tree depth exceeds allowed maximum of {max_depth}"
                )
            break

        stmt = select(ActivityType.activity_type_id, ActivityType.parent_id).where(
            ActivityType.activity_type_id.in_(list(current_level))
        )
        res = await session.execute(stmt)
        rows = res.fetchall()

        next_level: Set[int] = set()
        for aid, parent in rows:
            child_to_parent[int(aid)] = int(parent) if parent is not None else None
            if parent is not None and int(parent) not in all_ids:
                all_ids.add(int(parent))
                next_level.add(int(parent))

        current_level = next_level
        depth += 1

    # 2) загружаем все ActivityType для all_ids
    stmt = select(ActivityType).where(ActivityType.activity_type_id.in_(list(all_ids)))
    res = await session.execute(stmt)
    activities = res.scalars().all()

    # map id -> node dict
    node_map: Dict[int, Dict] = {}
    for activity in activities:
        node_map[int(activity.activity_type_id)] = {
            "activity_type_id": int(activity.activity_type_id),
            "name": activity.name,
            "parent_id": int(activity.parent_id) if activity.parent_id is not None else None,
            "children": []
        }

    # 3) связываем parent -> children (дети добавляются в parent)
    # используем child_to_parent
    for child_id, node in list(node_map.items()):
        parent_id = child_to_parent.get(child_id, node.get("parent_id"))
        if parent_id is not None and parent_id in node_map:
            node_map[parent_id]["children"].append(node_map[child_id])

    # 4) корневые узлы — те, у которых parent_id is None или parent не загружен
    roots = [
        n for nid, n in node_map.items()
        if n["parent_id"] is None or n["parent_id"] not in node_map
    ]

    # 5) сортировка для детерминизма
    def sort_rec(list_activities: List[Dict]):
        list_activities.sort(key=lambda x: (x.get("name") or "").lower())
        for item in list_activities:
            if item["children"]:
                sort_rec(item["children"])

    sort_rec(roots)
    return roots
