from sqlalchemy import PrimaryKeyConstraint, Column
from sqlalchemy.sql import sqltypes

from models import BaseModel


class SubwayRouteStation(BaseModel):
    __tablename__ = "subway_route_station"
    station_id = Column(sqltypes.String, primary_key=True)
    route_id = Column(sqltypes.Integer, nullable=False)
    station_name = Column(sqltypes.String, nullable=False)
    station_sequence = Column(sqltypes.Integer, nullable=False)
    cumulative_time = Column(sqltypes.Float, nullable=False)


class SubwayTimetable(BaseModel):
    __tablename__ = "subway_timetable"
    __table_args__ = (PrimaryKeyConstraint("station_id", "up_down_type", "weekday", "departure_time"),)
    station_id = Column(sqltypes.String, nullable=False)
    up_down_type = Column(sqltypes.String, nullable=False)
    weekday = Column(sqltypes.String, nullable=False)
    departure_time = Column(sqltypes.Time, nullable=False)
    terminal_station_id = Column(sqltypes.String, nullable=False)
