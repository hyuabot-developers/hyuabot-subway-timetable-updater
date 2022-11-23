import datetime

from sqlalchemy import PrimaryKeyConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    pass


class SubwayStation(BaseModel):
    __tablename__ = "subway_station"
    station_name: Mapped[str] = mapped_column(String(30), primary_key=True)


class SubwayRoute(BaseModel):
    __tablename__ = "subway_route"
    route_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_name: Mapped[str] = mapped_column(String(30), nullable=False)


class SubwayRouteStation(BaseModel):
    __tablename__ = "subway_route_station"
    station_id: Mapped[str] = mapped_column(primary_key=True)
    route_id: Mapped[str] = mapped_column(ForeignKey("subway_route.route_id"), nullable=False)
    station_name: Mapped[str] = mapped_column(ForeignKey("subway_station.station_name"))
    station_sequence: Mapped[int] = mapped_column(nullable=False)
    cumulative_time: Mapped[float] = mapped_column(nullable=False)


class SubwayTimetable(BaseModel):
    __tablename__ = "subway_timetable"
    __table_args__ = (PrimaryKeyConstraint("station_id", "up_down_type", "weekday", "departure_time"),)
    station_id: Mapped[str] = mapped_column(ForeignKey("subway_route_station.station_id"), nullable=False)
    up_down_type: Mapped[str] = mapped_column(nullable=False)
    weekday: Mapped[str] = mapped_column(nullable=False)
    departure_time: Mapped[datetime.time] = mapped_column(nullable=False)
    terminal_station_id: Mapped[str] = mapped_column(ForeignKey("subway_route_station.station_id"), nullable=False)
