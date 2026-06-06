import folium
from lang import *

def create_leaflet_map(center: list, zoom: int, start: list, end: list, path_geometry: list, turn_steps: list):
    """
    產生一個 folium 地圖 html  
    - center: [lat, lon]
    - zoom: int
    - start: [lat, lon, name]
    - end: [lat, lon, name]
    - path_geometry: [[lat1, lon1], [lat2, lon2], ...] (用於繪製完整路線軌跡)
    - turn_steps: [{"lat": lat, "lon": lon, "instruction": text, "short": text}, ...] (用於標示轉彎)
    """

    mymap = folium.Map(location=[center[0], center[1]], zoom_start=zoom, tiles="CartoDB positron")
    
    # Start
    start_coords = [start[0], start[1]]
    folium.Marker(
        location=start_coords,
        popup=f"<b>{start[2]}</b>",
        tooltip=text("map.start"),
        icon=folium.Icon(color="green", icon="home")
    ).add_to(mymap)
    
    # End
    end_coords = [end[0], end[1]]
    folium.Marker(
        location=end_coords,
        popup=f"<b>{end[2]}</b>",
        tooltip=text("map.arrived"),
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(mymap)
    
    # 繪製道路 (貼合道路的 PolyLine)
    folium.PolyLine(
        locations=path_geometry,
        color="royalblue",
        weight=6,
        opacity=0.8,
        tooltip=text("map.route")
    ).add_to(mymap)

    # 轉彎節點 marker
    for step in turn_steps:
        coords = [step["lat"], step["lon"]]
        folium.Marker(
            location=coords,
            popup=f"<b>{step['instruction']}</b>",
            tooltip=step["short"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mymap)
    
    # save as html
    output_filename = "project_map.html"
    mymap.save(output_filename)
    print(f"成功生成地圖網頁：{output_filename}")