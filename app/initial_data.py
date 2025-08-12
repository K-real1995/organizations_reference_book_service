import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_type import ActivityType
from app.models.building import Building
from app.models.organization import Organization
from app.models.phone import Phone

logger = logging.getLogger(__name__)


async def ensure_test_data(session: AsyncSession) -> None:
    result = await session.execute(select(Building).limit(1))
    existing = result.scalars().first()
    if existing:
        logging.info("Test data already exists — skipping seeding")
        return

    logger.info("Seeding test data...")

    food = ActivityType(name="Еда")
    meat = ActivityType(name="Мясная продукция", parent=food)
    dairy = ActivityType(name="Молочная продукция", parent=food)

    cars = ActivityType(name="Автомобили")
    trucks = ActivityType(name="Грузовые", parent=cars)
    passenger = ActivityType(name="Легковые", parent=cars)
    parts = ActivityType(name="Запчасти", parent=passenger)
    accessories = ActivityType(name="Аксессуары", parent=passenger)

    session.add_all([food, meat, dairy, cars, trucks, passenger, parts, accessories])
    await session.flush()

    # Создание зданий
    b1 = Building(address="г. Таллин, ул. Блюхера, 32/1", latitude=59.437, longitude=24.753)
    b2 = Building(address="г. Таллин, ул. Ленина, 1", latitude=59.430, longitude=24.750)
    session.add_all([b1, b2])
    await session.flush()

    # Организации
    org1 = Organization(name='ООО "Рога и Копыта"', building=b1, activities=[meat, dairy])
    org1.phones = [Phone(number="2-222-222"), Phone(number="3-333-333"), Phone(number="8-923-666-13-13")]

    org2 = Organization(name='Молочная Ферма', building=b2, activities=[dairy])
    org2.phones = [Phone(number="+37250123456")]

    org3 = Organization(name='АвтоМир', building=b2, activities=[parts, accessories])
    org3.phones = [Phone(number="+372509998877")]

    session.add_all([org1, org2, org3])

    try:
        await session.commit()
        logger.info("Seeding finished successfully")
    except IntegrityError:
        await session.rollback()
        logger.exception("Integrity error while seeding test data — rolled back")
    except Exception:
        await session.rollback()
        logger.exception("Unexpected error while seeding test data — rolled back")
        raise
