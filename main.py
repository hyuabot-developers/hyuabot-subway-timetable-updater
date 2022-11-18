import asyncio

from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

from models.subway import SubwayTimetable
from scripts.timetable import get_timetable_data
from utils.database import get_db_engine


async def main():
    connection = await get_db_engine()
    session_constructor = sessionmaker(bind=connection)
    session = session_constructor()
    if session is None:
        raise RuntimeError("Failed to get db session")
    session.execute(delete(SubwayTimetable))
    job_list = [
        get_timetable_data(session, "skyblue", 1004),
        get_timetable_data(session, "yellow", 1071),
    ]
    await asyncio.gather(*job_list)
    session.close()

if __name__ == '__main__':
    asyncio.run(main())
