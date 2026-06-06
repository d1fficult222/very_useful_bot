import discord
from discord.ext import commands
from aiohttp import web
import uuid, time, datetime, requests, os
from pathlib import Path
from lang import *
import generate_map

# Get location
BASE_DIR = Path(__file__).resolve().parent.parent
WEBPAGE_ROOT = BASE_DIR / "location_webpage"

LOCALMODE = False
WEBPAGE_URL = os.getenv("WEBPAGE_URL")
if not WEBPAGE_URL:
    print(text("locations.localhost"))
    WEBPAGE_URL = "http://localhost:8000/get_location.html"
    LOCALMODE = True
token_cache = {}
TOKEN_EXPIRES = 180  # Expires after 3 mins


# APIs
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/foot/"
EMAIL = os.getenv("EMAIL")
if not EMAIL:
    print(text("bot.email_notfound"))
    exit()
headers = {
    "User-Agent": f"VeryUsefulBot/1.11.0 ({EMAIL})"        
}


# User coordinates
user_coords = {}


class Locations(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.start_web_server())
    
    def cog_unload(self):
        self.bot.remove_command("get_location")

    @commands.hybrid_command(name="get_location", description=text("locations.get_location.description"))
    async def get_location(self, ctx: commands.Context):
        token = str(uuid.uuid4())
        
        token_cache[token] = {
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "expires": time.time() + TOKEN_EXPIRES
        }
        view = discord.ui.View()
        get_location_button = discord.ui.Button(
            label=text("locations.get_location"),
            url=f"{WEBPAGE_URL}?token={token}&guildID={ctx.guild.id}&channelID={ctx.channel.id}"
        )
        view.add_item(get_location_button)
        await ctx.send(text("locations.click_button"), view=view)

    @commands.hybrid_command(name="search", description="locations.search.description")
    async def search(self, ctx: commands.Context, location: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        data = self.location_search(location)
        if data and len(data) > 0:
            first_result = data[0]
            lat = first_result.get("lat")
            lon = first_result.get("lon")
            display_name = first_result.get("display_name")

            embed = discord.Embed(
                title=display_name,
                description=""
            )
            embed.add_field(name="lat", value=lat)
            embed.add_field(name="lon", value=lon)

            await ctx.send(embed=embed)

    @commands.hybrid_command(name="route", description="locations.route.description")
    async def route(self, ctx: commands.Context):
        # 測試：清大走到巨城
        start_lat, start_lon = 24.79368, 120.99561
        end_lat, end_lon = 24.80932, 120.97557
        center_lat = round((start_lat + end_lat)/2,4)
        center_lon = round((start_lon + end_lon)/2,4)

        result = self.get_walking_route(start_lat, start_lon, end_lat, end_lon, "清大", "巨城", center_lon, center_lat)

        # 檢查 API 調用是否成功
        if not result:
            await ctx.send(text("locations.route_failed"))
            return

        embed = discord.Embed(
            title=f"步行 {result['duration_min']} 分鐘，{result['distance_km']} 公里",
            description=f""
        )
        embed.add_field(name="from", value=f"{start_lat}, {start_lon}")
        embed.add_field(name="to", value=f"{end_lat}, {end_lon}")

        await ctx.send(embed=embed)

    async def handle_location_post(self, request):
        """
        接收到網頁 POST，發送經緯度的 embed 給使用者
        """
        try:
            data = await request.json()
            token = str(data.get("token"))
            lat = data.get("latitude")
            lon = data.get("longitude")
            
            # Missing parameters: 400 Error
            if not token or lat is None or lon is None:
                return web.Response(text=text("locations.missing_parameters"), status=400)
            
            # Invalid/expired token: 403 Forbidden
            if token not in token_cache:
                return web.Response(text=text("locations.invalid_token"), status=403)
            this_token = token_cache[token]
            if time.time() > this_token["expires"]:
                del token_cache[token]
                return web.Response(text=text("locations.token_expired"), status=403)

            # Get user id and channel
            user_id = this_token["user_id"]
            channel_id = this_token["channel_id"]

            # Save user location to cache
            user_coords[f"{user_id}"] = {
                "lon": lon,
                "lat": lat,
                "time": time.time()
            }

            
            # 傳送結果
            channel_id = this_token["channel_id"]
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title=text("locations.location"),
                        description=text("locations.get_location_description")
                    )
                    embed.add_field(name=text("locations.latitude"), value=lat)
                    embed.add_field(name=text("locations.longitude"), value=lon)
                    await channel.send(embed=embed)
                    del token_cache[token]
                    return web.Response(text=text("locations.susccess"), status=200)
            return web.Response(text=text("locations.channel_not_found"), status=404)
        except Exception as e:
            return web.Response(text=text("locations.general_error_1"), status=500)


    def location_search(self, location: str):
        """
        Use Nominatim API to search a location  
        Returns a json in dict
        """
        params = {
            "q": str(location),
            "format": "json",
            "addresdetails": 1
        }
        
        try:
            response = requests.get(NOMINATIM_URL, params=params, headers=headers)
            if response.status_code == 200:
                results = response.json()
                return results
            else:
                print(text("locations.nominatim.request_failed", {response.status_code}))
                return None
        except Exception as e:
            print(text("locations.nominatim.failed", {e}))
            return None


    def get_walking_route(self, start_lat, start_lon, end_lat, end_lon, start_name, end_name, center_lon, center_lat):
        coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"{OSRM_URL}{coords}?overview=full&geometries=geojson&steps=true"

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

                    for step in all_steps:
                        street_name = step.get("name", text("map.unknown_street"))
                        if street_name == "": street_name = text("map.unknown_street")
                        
                        maneuver = step.get("maneuver", {})
                        manuever_type = maneuver.get("type")  # turn, depart, arrive, ...
                        modifier = maneuver.get("modifier")   # left, right, straight, ...
                        
                        location = maneuver.get("location")
                        if not location or len(location) < 2:
                            continue
                        step_coords = (location[0], location[1])

                        if manuever_type == "depart":
                            instrcution = text("map.start_from", street_name)
                            instrcution_short = text("map.start")
                        elif manuever_type == "arrive":
                            instrcution = text("map.arrived_at", street_name)
                            instrcution_short = text("map.arrived")
                        elif manuever_type == "turn" or modifier is not None:
                            if modifier == "straight":
                                continue
                            instrcution = text(f"map.manuever.{modifier.replace(' ', '_')}.at", street_name)
                            instrcution_short = text(f"map.manuever.{modifier.replace(' ', '_')}")
                        else:
                            continue
                        
                        step_instructions[step_coords] = {
                            "instruction": instrcution,
                            "short": instrcution_short
                        }
                
                    path_coords = [[point[1], point[0]] for point in geometry]
                    turn_markers = [{
                        "lat": coord_key[1],
                        "lon": coord_key[0],
                        "instruction": info["instruction"],
                        "short": info["short"]
                    } for coord_key, info in step_instructions.items()]

                    generate_map.create_leaflet_map(
                        center=[center_lat, center_lon],
                        zoom=14,
                        start=[start_lat, start_lon, text("map.start_from", start_name)],
                        end=[end_lat, end_lon, text("map.arrived_at", end_name)],
                        path_geometry=path_coords,
                        turn_steps=turn_markers
                    )

                    return {
                        "duration_min": round(duration_sec/60, 2),
                        "distance_km": round(distance_m/1000, 2),
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


    async def start_web_server(self):
        """
        開始 Web server 
        """
        app = web.Application()
        app.router.add_static('/', str(WEBPAGE_ROOT), show_index=True)
        app.router.add_routes([
            web.post('/location', self.handle_location_post),
            web.options('/location', lambda r: web.Response(headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }))
        ])

        @web.middleware
        async def cors_middleware(request, handler):
            response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response
            
        app.middlewares.append(cors_middleware)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost' if LOCALMODE else '0.0.0.0', 8000)
        await site.start()
        print(text("locations.web_server_started"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Locations(bot))