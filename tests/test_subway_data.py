import asyncio
import datetime

import pytest
from sqlalchemy import delete
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from scripts.timetable import get_timetable_data
from models import BaseModel
from models import SubwayTimetable
from utils.database import get_db_engine
from tests.insert_subway_information import initialize_subway_data


class TestFetchRealtimeData:
    connection: Engine | None = None
    session_constructor = None
    session: Session | None = None

    @classmethod
    def setup_class(cls):
        cls.connection = get_db_engine()
        cls.session_constructor = sessionmaker(bind=cls.connection)
        # Database session check
        cls.session = cls.session_constructor()
        assert cls.session is not None
        # Migration schema check
        BaseModel.metadata.create_all(cls.connection)
        # Insert initial data
        asyncio.run(initialize_subway_data(cls.session))
        cls.session.commit()
        cls.session.close()

    @pytest.mark.asyncio
    async def test_fetch_realtime_data(self):
        connection = get_db_engine()
        session_constructor = sessionmaker(bind=connection)
        # Database session check
        session = session_constructor()
        # Get list to fetch
        session.execute(delete(SubwayTimetable))
        job_list = [
            get_timetable_data(session, "skyblue", 1004),
            get_timetable_data(session, "yellow", 1071),
        ]
        await asyncio.gather(*job_list)

        # Check if the data is inserted
        timetable_list = session.query(SubwayTimetable).all()
        for timetable_item in timetable_list:  # type: SubwayTimetable
            assert type(timetable_item.station_id) == str
            assert type(timetable_item.up_down_type) == str
            assert type(timetable_item.weekday) == str
            assert type(timetable_item.departure_time) == datetime.time
            assert type(timetable_item.terminal_station_id) == str
