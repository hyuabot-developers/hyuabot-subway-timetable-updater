import csv

from aiohttp import ClientTimeout, ClientSession
from sqlalchemy import insert, select, and_
from sqlalchemy.orm import Session

from models import SubwayTimetable, SubwayRouteStation


async def get_timetable_data(db_session: Session, route_id: int) -> None:
    timetable_items: list[dict] = []
    station_list: list[str] = []
    station_id_dict: dict[str, str] = {}
    station_name_dict: dict[str, str] = {
        "신인천": "인천", "한성대": "한성대입구", "경마공": "경마공원", "강남구": "강남구청",
        "남동인": "남동인더스파크", "매탄권": "매탄권선", "신길온": "신길온천", "4동운": "동대문역사문화공원",
        "수원시": "수원시청", "신수원": "수원", "4동대": "동대문", "로데오": "압구정로데오",
        "소래포": "소래포구", "총신대": "이수", "미아4": "미아사거리", "인천논": "인천논현",
        "구룡역": "구룡", "별가람": "별내별가람", "성신여": "성신여대입구", "4창동": "창동",
        "4충무": "충무로", "평촌동": "평촌", "숙대입": "숙대입구", "과천청": "과천정부청사",
        "4이촌": "이촌", "4서울": "서울역",
    }
    exclude_station_list: list[str] = ["별가람", "오남", "진접"]
    async with ClientSession(timeout=ClientTimeout(total=10)) as session:
        url = f"https://raw.githubusercontent.com/hyuabot-developers/hyuabot-subway-timetable/main/{route_id}.csv"
        async with session.get(url) as response:
            if response.status != 200:
                raise RuntimeError("Failed to get timetable data")
            reader = csv.reader((await response.text()).splitlines())
            for station, weekdays, heading, start, terminal, departure_time in reader:
                if station in exclude_station_list or terminal in exclude_station_list or start in exclude_station_list:
                    continue
                if station in station_name_dict:
                    station = station_name_dict[station]
                if terminal in station_name_dict:
                    terminal = station_name_dict[terminal]
                if start in station_name_dict:
                    start = station_name_dict[start]
                station_list.extend([station, start, terminal])
                timetable_items.append({
                    "station_name": station,
                    "up_down_type": heading,
                    "weekday": weekdays,
                    "departure_time": departure_time,
                    "start_station_name": start,
                    "terminal_station_name": terminal,
                })

    station_list = list(set(station_list))
    for station in station_list:
        station_query_statement = select(SubwayRouteStation.station_id).where(
            and_(SubwayRouteStation.station_name == station, SubwayRouteStation.route_id == route_id))
        station_id = ""
        for row in db_session.execute(station_query_statement):
            station_id = row[0]
            break
        if station_id == "":
            raise RuntimeError(f"Failed to get station id for {station}")
        station_id_dict[station] = station_id
    for timetable_item in timetable_items:
        timetable_item["station_id"] = station_id_dict[timetable_item["station_name"]]
        del timetable_item["station_name"]
        timetable_item["start_station_id"] = station_id_dict[timetable_item["start_station_name"]]
        del timetable_item["start_station_name"]
        timetable_item["terminal_station_id"] = station_id_dict[timetable_item["terminal_station_name"]]
        del timetable_item["terminal_station_name"]
    db_session.execute(insert(SubwayTimetable).values(timetable_items))
    db_session.commit()
