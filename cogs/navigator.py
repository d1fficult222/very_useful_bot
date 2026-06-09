import asyncio
import discord
from discord.ext import commands
from aiohttp import web
import uuid, time, os
from pathlib import Path
from lang import *
from navigator.navigator_utils import get_route, location_search



# Imperial units 的切換開關會在之後的更新中加上
IMPERIAL_UNITS = False


# Get location
BASE_DIR = Path(__file__).resolve().parent.parent
WEBPAGE_ROOT = BASE_DIR / "location_webpage"

LOCALMODE = False
WEBPAGE_URL = os.getenv("WEBPAGE_URL")
if not WEBPAGE_URL:
    print(text("locations.localhost"))
    WEBPAGE_URL = "http://localhost:8000/get_location.html"
    LOCALMODE = True
WEBPAGE_BASE = WEBPAGE_URL.split('?')[0].rsplit('/', 1)[0]
token_cache = {}
TOKEN_EXPIRES = 180  # Expires after 3 mins
route_cache = {}
ROUTE_EXPIRES = 12 * 3600  # Route map tokens valid for 12 hours


# User coordinates
user_coords = {}


def create_location_token(user_id: int, channel_id: int, pending_route: dict | None = None) -> str:
    token = str(uuid.uuid4())
    token_cache[token] = {
        "user_id": user_id,
        "channel_id": channel_id,
        "expires": time.time() + TOKEN_EXPIRES
    }
    if pending_route is not None:
        token_cache[token]["pending_route"] = pending_route
    return token


def build_location_view(token: str, guild_id: int, channel_id: int) -> discord.ui.View:
    view = discord.ui.View()
    get_location_button = discord.ui.Button(
        label=text("locations.get_location"),
        url=f"{WEBPAGE_URL}?token={token}&guildID={guild_id}&channelID={channel_id}"
    )
    view.add_item(get_location_button)
    return view


async def cleanup_route_files_once() -> None:
    now = time.time()
    expired = [token for token, info in route_cache.items() if now > info["expires"]]
    for token in expired:
        try:
            path = Path(route_cache[token]["file"])
            if path.exists():
                path.unlink()
        except Exception as cleanup_error:
            print(f"Route cleanup error: {cleanup_error}")
        finally:
            route_cache.pop(token, None)


async def send_route_result(start: dict, destination: dict, profile: str, send_message):
    token = str(uuid.uuid4())
    route_file = WEBPAGE_ROOT / f"{token}.html"

    await cleanup_route_files_once()

    result = get_route(
        {"lat": start["lat"], "lon": start["lon"], "name": start["name"]},
        {"lat": destination["lat"], "lon": destination["lon"], "name": destination["name"]},
        profile=profile,
        output_path=route_file
    )

    if not result:
        await send_message(text("locations.route_failed"))
        return False

    route_cache[token] = {
        "expires": time.time() + ROUTE_EXPIRES,
        "file": str(route_file)
    }

    duration = result["duration_text"]
    distance = result["distance_text"]
    steps_25 = result["step_by_step"][:25]

    embed = discord.Embed(
        title=f"{text(f'map.{profile}')} • {duration} • {distance}",
        description=f"{start['name']} → {destination['name']}"
    )
    for i, item in enumerate(steps_25):
        embed.add_field(name=str(i+1), value=item["text"])

    view = discord.ui.View()
    map_button = discord.ui.Button(
        label=text("locations.open_in_map"),
        url=f"{WEBPAGE_BASE}/{token}.html"
    )
    view.add_item(map_button)

    await send_message(embed=embed, view=view)
    return True


class Navigator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.start_web_server())
        bot.loop.create_task(self.cleanup_route_files())
    
    def cog_unload(self):
        self.bot.remove_command("get_location")

    @commands.hybrid_command(name="get_location", description=text("locations.get_location.description"))
    async def get_location(self, ctx: commands.Context):
        token = create_location_token(ctx.author.id, ctx.channel.id)
        view = build_location_view(token, ctx.guild.id, ctx.channel.id)
        await ctx.send(text("locations.click_button"), view=view)

    @commands.hybrid_command(name="search", description="locations.search.description")
    async def search_and_route(self, ctx: commands.Context, location: str):
        user = user_coords.get(str(ctx.author.id), None)
        if user is None:
            pending_route = {
                "action": "search",
                "location": location
            }
            token = create_location_token(ctx.author.id, ctx.channel.id, pending_route=pending_route)
            view = build_location_view(token, ctx.guild.id, ctx.channel.id)
            await ctx.send(text("locations.click_button"), view=view)
            return

        async def route(interaction: discord.Interaction, destination: dict, profile: str = "foot"):
            """
            從使用者位置規劃路徑至目的地  
            - destination: {'lat':25, 'lon':121, 'name': '地名'}  
            - profile: 'foot' 或 'car' 或 'bike'
            """
            start_lat, start_lon, start_name = user["lat"], user["lon"], text("locations.your_location")
            await send_route_result(
                {"lat": start_lat, "lon": start_lon, "name": start_name},
                destination,
                profile,
                interaction.response.send_message
            )
        
        if ctx.interaction:
            await ctx.interaction.response.defer()
        data = location_search(location, center_coord={"lat": user["lat"], "lon": user["lon"]})
        if data and len(data) > 0:
            first_result = data[0]
            lat = first_result.get("lat")
            lon = first_result.get("lon")
            display_name = first_result.get("display_name")

            embed = discord.Embed(
                title=display_name,
                description=""
            )
            embed.add_field(name=text("locations.latitude"), value=lat)
            embed.add_field(name=text("locations.longitude"), value=lon)

            class RouteSelect(discord.ui.Select):
                def __init__(self):
                    options = [
                        discord.SelectOption(label=text("map.foot"), value="foot"),
                        discord.SelectOption(label=text("map.car"), value="car"),
                        discord.SelectOption(label=text("map.bike"), value="bike"),
                    ]
                    super().__init__(placeholder=text("locations.find_route"), options=options)
                
                async def callback(self, interaction: discord.Interaction):
                    profile = self.values[0]
                    await route(interaction, {"lat": lat, "lon": lon, "name": location}, profile=profile)
            
            view = discord.ui.View()
            view.add_item(RouteSelect())
            await ctx.send(embed=embed, view=view)



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
            channel = self.bot.get_channel(channel_id) if channel_id else None
            if channel:
                embed = discord.Embed(
                    title=text("locations.location"),
                    description=text("locations.get_location_description")
                )
                embed.add_field(name=text("locations.latitude"), value=lat)
                embed.add_field(name=text("locations.longitude"), value=lon)
                await channel.send(embed=embed)

                pending_route = this_token.get("pending_route")
                if pending_route:
                    if pending_route.get("action") == "route":
                        destination = pending_route["destination"]
                        profile = pending_route["profile"]
                        start = {
                            "lat": lat,
                            "lon": lon,
                            "name": text("locations.your_location")
                        }
                        await send_route_result(start, destination, profile, channel.send)
                    elif pending_route.get("action") == "search":
                        search_location = pending_route["location"]
                        data = location_search(search_location, center_coord={"lat": lat, "lon": lon})
                        if data and len(data) > 0:
                            first_result = data[0]
                            dest_lat = first_result.get("lat")
                            dest_lon = first_result.get("lon")
                            display_name = first_result.get("display_name")

                            embed = discord.Embed(
                                title=display_name,
                                description=""
                            )
                            embed.add_field(name="lat", value=dest_lat)
                            embed.add_field(name="lon", value=dest_lon)

                            class RouteSelect(discord.ui.Select):
                                def __init__(self):
                                    options = [
                                        discord.SelectOption(label=text("map.foot"), value="foot"),
                                        discord.SelectOption(label=text("map.car"), value="car"),
                                        discord.SelectOption(label=text("map.bike"), value="bike"),
                                    ]
                                    super().__init__(placeholder=text("locations.find_route"), options=options)
                                
                                async def callback(self, interaction: discord.Interaction):
                                    profile = self.values[0]
                                    await send_route_result(
                                        {"lat": lat, "lon": lon, "name": text("locations.your_location")},
                                        {"lat": dest_lat, "lon": dest_lon, "name": search_location},
                                        profile,
                                        interaction.response.send_message
                                    )
                            
                            view = discord.ui.View()
                            view.add_item(RouteSelect())
                            await channel.send(embed=embed, view=view)

                del token_cache[token]
                return web.Response(text=text("locations.susccess"), status=200)
            return web.Response(text=text("locations.channel_not_found"), status=404)
        except Exception as e:
            return web.Response(text=text("locations.general_error_1"), status=500)

    async def cleanup_route_files(self):
        while True:
            await asyncio.sleep(60)
            await cleanup_route_files_once()

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
    await bot.add_cog(Navigator(bot))