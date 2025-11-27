import discord
from discord.ext import commands, tasks
from discord import app_commands, File
from discord.ui import Button, View
import datetime, json, io
import settings
from user_options import get_user_options
from lang import *
from PIL import Image, ImageDraw, ImageFont


class TimeTable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("settable")
        self.bot.remove_command("timetable")


    # Import/Initialize timetable
    class ImportWindow(discord.ui.Modal, title=text("modal.timetable.title")):
        def __init__(self, cog):
            super().__init__()
            self.cog = cog

        timetable_input = discord.ui.TextInput(
            label=text("modal.timetable.label"),
            style=discord.TextStyle.paragraph,
            placeholder=text("modal.timetable.placeholder"),
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            try:
                timetable = json.loads(self.timetable_input.value)
                with open(f"assets/timetable/{interaction.user.id}.json", "w", encoding="utf-8") as f:
                    json.dump(timetable, f, ensure_ascii=False, indent=4)
                await interaction.response.send_message(text("modal.timetable.success"), ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(text("modal.timetable.error", e), ephemeral=True)

    @app_commands.command(name="settable", description=text("cmd.settable.description"))
    async def settable(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.ImportWindow(self))


    # Print out timetable
    @app_commands.command(name="timetable", description=text("cmd.timetable.description"))
    async def timetable(self, interaction: discord.Interaction):
        try:
            with open(f"assets/timetable/{interaction.user.id}.json", "r", encoding="utf-8") as f:
                timetable = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message(text("cmd.timetable.notfound", interaction.user.mention), ephemeral=True)
            return
        

        # Image Setup
        SIZE = get_user_options(interaction.user.id, "CalendarBlockSize")
        MARGIN = get_user_options(interaction.user.id, "CalendarBlockMargin")
        CELL_COLOR = get_user_options(interaction.user.id, "CalendarBackgroundColor")
        OCCUPIED_COLOR = get_user_options(interaction.user.id, "CalendarColor1")
        TEXT_COLOR = get_user_options(interaction.user.id, "CalendarFontColor1")
        # Draw image
        WEEKDAYS = 5 + 1  # plus one for col 1 (time intervals)
        BLOCKS = 13 + 1  # plus one for row 1 (mon, tue, ...)
        WIDTH = SIZE
        HEIGHT = SIZE
        FONT_SIZE = round(SIZE * 3 / 5)
        def load_font(size):
            candidates = [
                r"C:\Windows\Fonts\msjh.ttc",                            # Microsoft JhengHei（Windows）
                r"C:\Windows\Fonts\msjhbd.ttf",                          # Microsoft JhengHei Bold
                r"C:\Windows\Fonts\mingliu.ttc",                         # PMingLiU（繁體）
                r"C:\Windows\Fonts\DFKai-SB.ttf",                        # 標楷體（常見）
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",# Noto CJK（Linux）
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "arial.ttf",
            ]
            for path in candidates:
                try:
                   return ImageFont.truetype(path, size)
                except Exception:
                    try:
                        return ImageFont.truetype(path.split("\\")[-1], size)
                    except Exception:
                        continue
            return ImageFont.load_default()

        font = load_font(FONT_SIZE // 3)
        image_width = (WIDTH + MARGIN) * WEEKDAYS - MARGIN
        image_height = (HEIGHT + MARGIN) * BLOCKS - MARGIN
        image = Image.new("RGB", (image_width, image_height), color=CELL_COLOR)
        draw = ImageDraw.Draw(image)
        table = timetable["cells"]
        for i in range(WEEKDAYS):
            for j in range(BLOCKS):
                x1 = i * (WIDTH + MARGIN)
                y1 = j * (HEIGHT + MARGIN)
                x2 = x1 + WIDTH
                y2 = y1 + HEIGHT
                if i == 0:
                    # Column 1, show time durations
                    try:
                        time_start = timetable["timeArray"][j-1]
                        time_end_min = timetable["timeArray"][j-1][1] + timetable["interval"]
                        time_end_hour = timetable["timeArray"][j-1][0]
                        while time_end_min >= 60:
                            time_end_min -= 60
                            time_end_hour += 1
                            if time_end_hour >= 24: time_end_hour = 0
                        time_end = [time_end_hour, time_end_min]
                    except: pass
                    if j != 0:
                        txt = f"{j}\n{time_start[0]:02d}:{time_start[1]:02d}\n{time_end[0]:02d}:{time_end[1]:02d}"
                        draw.rectangle([x1, y1, x2, y2], fill=CELL_COLOR)
                        txt_x = x1 + MARGIN // 2
                        txt_y = y1 + MARGIN // 2
                        draw.text((txt_x, txt_y), txt, TEXT_COLOR, font=font)
                else:
                    # Table content
                    if j == 0:
                        txt = ["MON", "TUE", "WED", "THU", "FRI"][i-1]
                        draw.rectangle([x1, y1, x2, y2], fill=CELL_COLOR)
                        bbox = font.getbbox(txt)
                        txt_width = bbox[2] - bbox[0]
                        txt_height = bbox[3] - bbox[1]
                        txt_x = x1 + (WIDTH - txt_width) // 2
                        txt_y = y1 + (HEIGHT - txt_height) // 2
                        draw.text((txt_x, txt_y), txt, fill=TEXT_COLOR, font=font)
                    else:
                        txt = table[i-1][j-1]
                        draw.rectangle([x1, y1, x2, y2], fill=OCCUPIED_COLOR if txt else CELL_COLOR)
                        txt_x = x1 + MARGIN // 2
                        txt_y = y1 + MARGIN // 2
                        draw.text((txt_x, txt_y), txt, fill=CELL_COLOR if txt else TEXT_COLOR, font=font)

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')    
        buffer.seek(0)

        await interaction.response.send_message(file=File(buffer, text("timetable.image.png")))

    # Show next class
    @app_commands.command(name="next_class", description=text("cmd.next_class.description"))
    async def next_class(self, interaction: discord.Interaction):
        try:
            with open(f"assets/timetable/{interaction.user.id}.json", "r", encoding="utf-8") as f:
                timetable = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message(text("cmd.next_class.notfound"), ephemeral=True)
            return
        
        # Check current day and time
        now = datetime.datetime.now()
        weekday = now.weekday()  # Monday is 0 and Sunday is 6
        current_time = now.time().hour * 60 + now.time().minute
        time_array = [i[0]*60 + i[1] for i in timetable["timeArray"]]
        for i in range(len(time_array)):
            if current_time > time_array[i]:
                break
                
        # Find next class
        next_found = False
        if weekday <= 4:
            today_schedule = timetable["cells"][weekday]
            times = timetable["timeArray"]
            for j in range(i, len(today_schedule)):
                if today_schedule[j] != "":
                    if times[j][0] * 60 + times[j][1] > current_time:
                        next_found = True
                        break
        
        # Send message
        if next_found:
            name, instructor, location = today_schedule[j].split("\n") 
            embed = discord.Embed(
                title=text("timetable.next.class", name), 
                description=text("timetable.next.time", ':'.join(map(str, timetable["timeArray"][j])))
            )
            if location != '-': embed.add_field(name=text("timetable.location"), value=location)
            if instructor != '-': embed.add_field(name=text("timetable.instructor"), value=instructor)

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(text("timetable.nonext"))


 


async def setup(bot):
    await bot.add_cog(TimeTable(bot))