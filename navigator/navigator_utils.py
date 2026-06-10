import os
from pathlib import Path
import requests
from lang import *
from navigator import generate_map
import settings

# Imperial units 的切換開關會在之後的更新中加上
IMPERIAL_UNITS = False

BASE_DIR = Path(__file__).resolve().parent.parent
WEBPAGE_ROOT = BASE_DIR / "location_webpage"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1"
EMAIL = os.getenv("EMAIL")
if not EMAIL:
    print(text("bot.email_notfound"))
    exit()
headers = {
    "User-Agent": f"VeryUsefulBot/1.11.0 ({EMAIL})"
}


def location_search(location: str, center_coord: dict = None):
    """
    Use Nominatim API to search a location.  
    Returns a list of json results.  
    - location: 搜尋的地點名稱
    - center_coord: 可選，格式 {"lat": 25.00, "lon": 121.00}，將限制搜尋範圍在該座標方圓約 10km 內
    """
    params = {
        "q": str(location),
        "format": "json",
        "addressdetails": 1,
        "countrycodes": settings.country_code,
        "limit": 20,
    }
    
    # 如果有中心座標，先在 10km 範圍內搜尋
    if center_coord and "lat" in center_coord and "lon" in center_coord:
        lat, lon = center_coord["lat"], center_coord["lon"]
        offset = 0.09
        viewbox = f"{lon - offset},{lat - offset},{lon + offset},{lat + offset}"
        params["viewbox"] = viewbox
        params["bounded"] = 1

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers)
        if response.status_code == 200:
            results = response.json()
            
            # 如果有指定搜尋範圍但沒有結果，解除限制重新搜尋
            if center_coord and not results:
                params.pop("viewbox", None)
                params.pop("bounded", None)
                
                response = requests.get(NOMINATIM_URL, params=params, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(text("locations.nominatim.request_failed", {response.status_code}))
                    return None
            
            return results
        else:
            print(text("locations.nominatim.request_failed", {response.status_code}))
            return None
    except Exception as e:
        print(text("locations.nominatim.failed", {e}))
        return None


def get_route(start_loc: dict, end_loc: dict, profile: str = "foot", output_path: Path = WEBPAGE_ROOT / "project_map.html"):
    """
    輸入:
    - start_loc/end_loc 格式: {"lat": 25.0478, "lon": 121.5170, "name": "台北車站"}
    - profile 請選擇: "foot" (步行), "car" (開車), "bike" (騎車)，預設為步行
    - output_path: route map HTML 輸出的完整路徑

    輸出:
    - {"distance_text", "duration_text", "step_by_step", "coordinates_lon_lat"}
    """
    start_lat, start_lon, start_name = float(start_loc["lat"]), float(start_loc["lon"]), str(start_loc["name"])
    end_lat, end_lon, end_name = float(end_loc["lat"]), float(end_loc["lon"]), str(end_loc["name"])
    if profile not in ["foot", "car", "bike"]:
        profile = "foot"

    center_lat = (start_lat + end_lat) / 2
    center_lon = (start_lon + end_lon) / 2
    coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"{OSRM_URL}/{profile}/{coords}?overview=full&geometries=geojson&steps=true"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok":
                route = data["routes"][0]
                duration_sec = route.get("duration", 0)
                distance_m = route.get("distance", 0)
                geometry = route["geometry"]["coordinates"]
                all_steps = route["legs"][0]["steps"]

                step_instructions = {}
                text_instructions_list = []
                for step in all_steps:
                    street_name = step.get("name", text("map.unknown_street"))
                    if street_name == "":
                        street_name = text("map.unknown_street")

                    maneuver = step.get("maneuver", {})
                    maneuver_type = maneuver.get("type")
                    modifier = maneuver.get("modifier")
                    location = maneuver.get("location")
                    if not location or len(location) < 2:
                        continue
                    step_coords = (location[0], location[1])

                    if maneuver_type == "depart":
                        instruction = text("map.start_from", street_name)
                        instruction_short = text("map.start")
                    elif maneuver_type == "arrive":
                        instruction = text("map.arrived_at", street_name)
                        instruction_short = text("map.arrived")
                    elif maneuver_type == "turn" or modifier is not None:
                        if modifier == "straight":
                            continue
                        instruction = text(f"map.manuever.{modifier.replace(' ', '_')}.at", street_name)
                        instruction_short = text(f"map.manuever.{modifier.replace(' ', '_')}")
                    else:
                        continue

                    step_instructions[step_coords] = {
                        "instruction": instruction,
                        "short": instruction_short
                    }
                    text_instructions_list.append({
                        "text": instruction,
                        "lat": step_coords[1],
                        "lon": step_coords[0]
                    })

                path_coords = [[point[1], point[0]] for point in geometry]
                turn_markers = [{
                    "lat": coord_key[1],
                    "lon": coord_key[0],
                    "instruction": info["instruction"],
                    "short": info["short"]
                } for coord_key, info in step_instructions.items()]

                minutes = round(duration_sec / 60)
                hours = minutes // 60
                duration_text = (
                    f"{hours} {text('map.hours')} {minutes-hours*60} {text('map.minutes')}"
                    if hours > 0
                    else f"{minutes} {text('map.minutes')}"
                )
                meters = round(distance_m)
                if not IMPERIAL_UNITS:
                    kilometers = round(meters / 1000, 2)
                    km_unit = text('map.kilometers') if text('map.kilometers') != 'map.kilometers' else text('map.kilometres')
                    m_unit = text('map.meters') if text('map.meters') != 'map.meters' else text('map.metres')
                    distance_text = f"{kilometers} {km_unit}" if kilometers > 1 else f"{meters} {m_unit}"
                else:
                    feet = round(meters * 3.28)
                    miles = round(feet / 5280, 2)
                    distance_text = f"{miles} {text('map.miles')}" if miles > 1 else f"{feet} {text('map.feet')}"

                route_summary = {
                    "distance_text": distance_text,
                    "duration_text": duration_text,
                    "step_by_step": text_instructions_list
                }

                generate_map.create_leaflet_map(
                    center=[center_lat, center_lon],
                    zoom=14,
                    start=[start_lat, start_lon, text("map.start_from", start_name)],
                    end=[end_lat, end_lon, text("map.arrived_at", end_name)],
                    path_geometry=path_coords,
                    turn_steps=turn_markers,
                    route_info=route_summary,
                    profile=profile,
                    output_path=output_path
                )

                return {
                    "distance_text": distance_text,
                    "duration_text": duration_text,
                    "duration_minutes": minutes,
                    "step_by_step": text_instructions_list,
                    "coordinates_lon_lat": geometry,
                }
            else:
                print(text("locations.osrm.error", data.get("code")))
                return None
        else:
            print(text("locations.osrm.request_failed", response.status_code))
            return None
    except Exception as e:
        print(text("locations.osrm.failed", {e}))
        return None
