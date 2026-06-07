import asyncio
import discord
from discord.ext import commands
from aiohttp import web
import uuid, time, os
from pathlib import Path
from lang import *
from locations.location_utils import get_route, location_search



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


class Locations(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.start_web_server())
        bot.loop.create_task(self.cleanup_route_files())
    
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
        
        # 測試
        start_lat, start_lon, start_name = 24.80932, 120.97557, "巨城"
        end_lat, end_lon, end_name = 25.08093, 121.23667, "桃園機場"
        token = str(uuid.uuid4())
        route_file = WEBPAGE_ROOT / f"{token}.html"

        await self.cleanup_route_files_once()

        profile = "foot"
        result = self.get_route(
            {"lat": start_lat, "lon": start_lon, "name": start_name},
            {"lat": end_lat, "lon": end_lon, "name": end_name},
            profile=profile,
            output_path=route_file
        )

        if not result:
            await ctx.send(text("locations.route_failed"))
            return

        route_cache[token] = {
            "expires": time.time() + ROUTE_EXPIRES,
            "file": str(route_file)
        }
        
        duration = result["duration_text"]
        distance = result["distance_text"]
        steps_25 = result["step_by_step"][:25]

        embed = discord.Embed(
            title=f"{text(f'map.{profile}')} • {duration} • {distance}",
            description=f"{start_name} → {end_name}"
        )
        for i, item in enumerate(steps_25):
            embed.add_field(name=str(i+1), value=item["text"])

        view = discord.ui.View()
        map_button = discord.ui.Button(
            label=text("locations.open_map") if text("locations.open_map") != "locations.open_map" else "Open Map",
            url=f"{WEBPAGE_BASE}/{token}.html"
        )
        view.add_item(map_button)

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

    async def cleanup_route_files_once(self):
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

    async def cleanup_route_files(self):
        while True:
            await asyncio.sleep(60)
            await self.cleanup_route_files_once()

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