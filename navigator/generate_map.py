import folium
from folium import Element
from lang import *

def create_leaflet_map(
        center: list,
        zoom: int,
        start: list,
        end: list,
        path_geometry: list,
        turn_steps: list,
        route_info: dict,
        profile: str,
        output_path: str = "project_map.html"
):
    """
    產生一個 folium 地圖 html  
    - center: [lat, lon]
    - zoom: int
    - start: [lat, lon, name]
    - end: [lat, lon, name]
    - path_geometry: [[lat1, lon1], [lat2, lon2], ...] (用於繪製完整路線軌跡)
    - turn_steps: [{"lat": lat, "lon": lon, "instruction": text, "short": text}, ...] (用於標示轉彎)
    - route_info: {"duration_min": float, "distance_km": float, "step_by_step": list} (用於顯示總覽)
    - profile 請選擇: "foot" (步行), "car" (開車), "bike" (騎車)，預設為步行
    - output_path: 輸出的 html 檔案路徑
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
        opacity=0.6,
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
        
    # Sidebar
    map_js_name = mymap.get_name()
    steps_list_html = ""
    
    for i, step in enumerate(route_info.get("step_by_step", [])):
        lat = step["lat"]
        lon = step["lon"]
        step_text = step["text"]
        
        steps_list_html += f"""
        <li onclick="focusMap({lat}, {lon})" 
            style="padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; transition: 0.2s;"
            onmouseover="this.style.backgroundColor='#f0f8ff'" 
            onmouseout="this.style.backgroundColor='transparent'">
            <b>{i+1}.</b> {step_text}
        </li>
        """

    sidebar_html = f"""
    <style>
        #navigation-sidebar {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 9999;
            background: white;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            width: 320px;
            max-height: 80vh;
            overflow-y: auto;
            font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        #navigation-sidebar::-webkit-scrollbar {{ width: 6px; }}
        #navigation-sidebar::-webkit-scrollbar-thumb {{ background-color: #ccc; border-radius: 3px; }}
    </style>

    <div id="navigation-sidebar">
        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
            <span style="font-size: 22px; font-weight: bold; color: #2c3e50;">
                {route_info.get('duration_text', text('map.unknown_duration'))}
            </span><br>
            <span style="color: #6c757d; font-size: 14px;">
                {text(f'map.{profile}')} • {route_info.get('distance_text', text('map.unknown_distance'))}
            </span>
        </div>
        
        <ul style="list-style: none; padding-left: 0; margin: 0; font-size: 14px; color: #444;">
            {steps_list_html}
        </ul>
    </div>
    <script>
        function focusMap(lat, lon) {{
            {map_js_name}.flyTo([lat, lon], 17, {{
                animate: true,
                duration: 1
            }});
            // 動畫 1s, 放大 17
        }}
    </script>
    """
    
    mymap.get_root().html.add_child(Element(sidebar_html))

    mymap.save(str(output_path))
    print(text("map.generated", output_path))