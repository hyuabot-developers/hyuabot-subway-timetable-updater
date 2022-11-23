import asyncio
import csv

from aiohttp import ClientTimeout, ClientSession
from sqlalchemy import insert, select, and_
from sqlalchemy.orm import Session

from models import SubwayTimetable, SubwayRouteStation


async def get_timetable_data(db_session: Session, route_name: str, route_id: int) -> None:
    timetable_items: list[dict] = []
    terminal_station_items: list[str] = []
    terminal_station_id: dict[str, str] = {}
    station_name_dict: dict[str, str] = {
        "신인천": "인천",
        "한성대": "한성대입구",
    }

    station_query_statement = select(SubwayRouteStation.station_id).where(
        and_(SubwayRouteStation.station_name == "한대앞" and SubwayRouteStation.route_id == route_id))
    start_station_id = ""
    for row in db_session.execute(station_query_statement):
        start_station_id = row[0]
        break
    if not start_station_id:
        raise RuntimeError("Failed to get start station id")
    for weekday in ["weekdays", "weekends"]:
        for heading in ["up", "down"]:
            url = ""
            try:
                url = "https://raw.githubusercontent.com/hyuabot-developers/" \
                      f"hyuabot-subway-timetable/main/{route_name}/weekdays/{heading}.csv"
                timeout = ClientTimeout(total=3.0)
                async with ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        reader = csv.reader((await response.text()).splitlines())
                        for terminal_station_name, departure_time in reader:
                            if terminal_station_name in station_name_dict.keys():
                                terminal_station_name = station_name_dict[terminal_station_name]
                            timetable_items.append({
                                "station_id": start_station_id,
                                "weekday": weekday,
                                "up_down_type": heading,
                                "departure_time": f"{departure_time}+09:00",
                                "terminal_station": terminal_station_name,
                            })
                            terminal_station_items.append(terminal_station_name)
            except asyncio.exceptions.TimeoutError:
                print("TimeoutError")
            except AttributeError:
                print("AttributeError", url)
    for station_name in list(set(terminal_station_items)):
        station_item_query = select(SubwayRouteStation.station_id).where(
            and_(SubwayRouteStation.station_name == station_name, SubwayRouteStation.route_id == route_id))
        station_id, = db_session.execute(station_item_query).fetchone()
        if station_id is None:
            raise RuntimeError("Failed to get station id")
        terminal_station_id[station_name] = station_id
    for timetable_item in timetable_items:
        timetable_item["station_id"] = start_station_id
        timetable_item["terminal_station_id"] = terminal_station_id[timetable_item["terminal_station"]]
        del timetable_item["terminal_station"]
    db_session.execute(insert(SubwayTimetable).values(timetable_items))
    db_session.commit()
