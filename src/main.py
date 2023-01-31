import asyncio

from sqlalchemy import delete
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from models import SubwayTimetable
from scripts.timetable import get_timetable_data
from utils.database import get_db_engine, get_master_db_engine


async def main():
    connection = get_db_engine()
    session_constructor = sessionmaker(bind=connection)
    session = session_constructor()
    if session is None:
        raise RuntimeError("Failed to get db session")
    try:
        await execute_script(session)
    except OperationalError:
        connection = get_master_db_engine()
        session_constructor = sessionmaker(bind=connection)
        session = session_constructor()
        await execute_script(session)


async def execute_script(session):
    session.execute(delete(SubwayTimetable))
    job_list = [
        get_timetable_data(session, 1004),
        get_timetable_data(session, 1071),
    ]
    await asyncio.gather(*job_list)
    session.close()

if __name__ == '__main__':
    asyncio.run(main())
