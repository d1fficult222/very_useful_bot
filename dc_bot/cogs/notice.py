import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice, Range
from typing import Optional
import datetime, json, asyncio
import settings
from lang import *



with open("assets/notice.json", "r") as f:
    """
    All the notice events are stored here
    """
    events = json.load(f)

def sync_json():
    """
    Syncs event list with assets/notice.json file
    """
    with open("assets/notice.json", "w") as f:
        f.write(json.dumps(events, indent=4))

def pre_zero(tofix: int) -> str:
    """
    Prefix zero
    Useful for mm:ss formats
    Example: 9 (int) -> '09' (str)
    """
    return f"{tofix:02d}"

def check_notice():
    """
    Handles embed message
    """
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    weekday = now.isoweekday()
    if len(events) == 0: return None
    success = False
    returnlist = []
    for i in events[:]:
        if i["note"] == 0:
            # notice_at, notice_after
            success = i["year"] == year and i["month"] == month and i["day"] == day and i["hour"] == hour and i["minute"] == minute      
        elif i["note"] == 2:
            # routine
            success = i["weekday"] == weekday and i["hour"] == hour and i["minute"] == minute
        else:
            # note
            continue
    if success:
        embed = discord.Embed(
            title=text("notice.title"),
            description=f'## {i["event"]}',
            color=settings.Colors.notice,
            timestamp=datetime.datetime.now()
        )
        if i["note"] == 2:
            if i['location']: embed.add_field(name=text("notice.location"), value=i['location'])
        channel = i["channel"]
        user = i["user"]
        if i["note"] == 0: events.remove(i)
        sync_json()
        returnlist.append([user, channel, embed])
        return returnlist
    else:
        return None

class DropDown(discord.ui.Select):
    """
    Dropdown menu for 'notice delete'
    """
    def __init__(self, user_id):
        selects = []
        for i in events:
            if i['user'] != user_id: continue
            if i['note'] == 0:
                # notice_at, notice_after  
                selects.append(discord.SelectOption(
                    label=f"{text('notice.type0')}: {i['event']}",
                    description=f"{i['year']}/{i['month']}/{i['day']} {pre_zero(i['hour'])}:{pre_zero(i['minute'])}",
                    value=i['event'])
                    )
            elif i['note'] == 1:
                # note
                selects.append(discord.SelectOption(
                    label=f"{text('notice.type1')}: {i['event']}",
                    description=f"{i['year']}/{i['month']}/{i['day']} {pre_zero(i['hour'])}:{pre_zero(i['minute'])}",
                    value=i['event'])
                    )
            else:
                # routine
                selects.append(discord.SelectOption(
                    label=f"{text('notice.type2')}: {i['event']}",
                    description=f"{text('notice.'+str(Notice.week[i['weekday']]))} {pre_zero(i['hour'])}:{pre_zero(i['minute'])}",
                    value=i['event'])
                    )
        selects.append(discord.SelectOption(label=text("cmd.notice_delete.cancel"), description=text("cmd.notice_delete.cancel_des"), value="CANCEL"))
        super().__init__(placeholder=text("cmd.notice_delete.placeholder"), min_values=1, max_values=1, options=selects)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "CANCEL":
            await interaction.response.defer()
            await interaction.delete_original_response()
            return
        for i in events:
            if i["event"] == self.values[0]:
                events.remove(i)
                sync_json()
                await interaction.response.defer()
                await interaction.edit_original_response(content=text("cmd.notice_delete.deleted",self.values[0]), view=None)
                return
        await interaction.response.defer()
        await interaction.edit_original_response(content=text("cmd.notice_delete.error"), view=None)

class DropDownView(discord.ui.View):
    """
    Dropdown menu view for 'notice delete'
    """
    def __init__(self, user_id):
        super().__init__()
        self.add_item(DropDown(user_id=user_id))



class Notice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notice_loop.start()

    def cog_unload(self):
        self.notice_loop.cancel()

    @tasks.loop(minutes=1)
    async def notice_loop(self):
        result = check_notice()   # [user: int, channel: int, embed: discord.Embed]
        if result:
            for i in result:
                user = await self.bot.fetch_user(i[0])
                await user.send(f"<@{i[0]}>", embed=i[2])

    @notice_loop.before_loop
    async def before_notice_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now()
        seconds_to_wait = 60 - now.second
        await asyncio.sleep(seconds_to_wait)



    @app_commands.command(name="notice_after", description=text("cmd.notice_after.description"))
    @app_commands.describe(event=text("cmd.notice_after.event"), time=text("cmd.notice_after.time"), unit=text("cmd.notice_after.unit"))
    @app_commands.choices(
        unit=[
            Choice(name=text("cmd.notice_after.minute"), value="m"),
            Choice(name=text("cmd.notice_after.hour"), value="h"),
            Choice(name=text("cmd.notice_after.days"), value="d")
        ]
    )
    async def notice_after(self, interaction: discord.Interaction, event: str, time: Range[int, 1, 60], unit: Choice[str]):
        for i in events:
            if i["event"] == event:
                await interaction.response.send_message(text("cmd.notice_after.exist"))
                return
        now = datetime.datetime.now()
        match unit.value:
            case "m": target = now + datetime.timedelta(minutes=time)
            case "h": target = now + datetime.timedelta(hours=time)
            case "d": target = now + datetime.timedelta(days=time)
        tar = {
            "note": 0,
            "year": target.year,
            "month": target.month,
            "day": target.day,
            "hour": target.hour,
            "minute": target.minute,
            "event": event,
            "channel": interaction.channel_id,
            "user": interaction.user.id
        }
        events.append(tar)
        sync_json()
        match unit.value:
            case "m": after = text("cmd.notice_after.after_mins",time)
            case "h": after = text("cmd.notice_after.after_hours",time)
            case "d": after = text("cmd.notice_after.after_days",time)
        embed = discord.Embed(
            title=text("cmd.notice_after.set"),
            description=f"## {event}",
            timestamp=datetime.datetime.now(),
            color=settings.Colors.notice
        )
        embed.add_field(name=text("cmd.notice_after.trigger"), value=after)
        embed.add_field(name=text("cmd.notice_after.trigger_time"), value=f"{target.year}/{target.month}/{target.day} {pre_zero(target.hour)}:{pre_zero(target.minute)}")
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="notice_at", description=text("cmd.notice_at.description"))
    @app_commands.describe(event=text("cmd.notice_at.event"), year=text("cmd.notice_at.year"), month=text("cmd.notice_at.month"), day=text("cmd.notice_at.day"), hour=text("cmd.notice_at.hour"), minute=text("cmd.notice_at.minute"))
    @app_commands.choices(
        year=[Choice(name=i, value=i) for i in range(2025, 2030)],
        month=[Choice(name=i, value=i) for i in range(1, 13)],
    )
    async def notice_at(self, interaction: discord.Interaction, event: str, year: Choice[int], month: Choice[int], day: Range[int, 1, 31], hour: Range[int, 0, 24], minute: Range[int, 0, 60]):
        for i in events:
            if i["event"] == event:
                await interaction.response.send_message(text("cmd.notice_at.exist"))
                return
        tar = {
            "note": 0,
            "year": year.value,
            "month": month.value,
            "day": day,
            "hour": hour,
            "minute": minute,
            "event": event,
            "channel": interaction.channel_id,
            "user": interaction.user.id
        }
        events.append(tar)
        sync_json()
        embed = discord.Embed(
            title=text("cmd.notice_at.set"),
            description=f"## {event}",
            timestamp=datetime.datetime.now(),
            color=settings.Colors.notice
        )
        embed.add_field(name=text("cmd.notice_at.trigger_time"), value=f"{year.value}/{month.value}/{day} {pre_zero(hour)}:{pre_zero(minute)}")
        await interaction.response.send_message(embed=embed)

   

    week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    @app_commands.command(name="notice_routine", description=text("notice.routine.description"))
    @app_commands.describe(event=text("notice.routine.event"), location=text("notice.routine.location"), weekday=text("notice.routine.weekday"), hour=text("notice.hour"), minute=text("notice.minute"))
    @app_commands.choices(
        weekday=[Choice(name=text(f"notice.{w}"), value=idx+1) for idx, w in enumerate(week)]
    )
    async def notice_routine(self, interaction: discord.Interaction, event: str, location: Optional[str], weekday: Choice[int], hour: Range[int, 0, 24], minute: Range[int, 0, 60]):
        for ev in events:
            if ev["event"] == event:
                await interaction.response.send_message(text("cmd.notice_at.exist"))
                return
        tar = {
            "note": 2,
            "location": location if location else '',
            "weekday": weekday.value,
            "hour": hour,
            "minute": minute,
            "event": event,
            "channel": interaction.channel_id,
            "user": interaction.user.id
        }
        events.append(tar)
        sync_json()
        embed = discord.Embed(
            title=text("notice.routine.set"),
            description=f"## {event}\n",
            color=settings.Colors.notice
        )
        embed.add_field(name=text("notice.routine.trigger_time"), value=f"{text('notice.'+str(self.week[weekday.value-1]))} {pre_zero(hour)}:{pre_zero(minute)}")
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="notice_delete", description=text("cmd.notice_delete.description"))
    async def notice_delete(self, interaction: discord.Interaction):
        await interaction.response.send_message(text("cmd.notice_delete.select"), view=DropDownView(interaction.user.id), delete_after=15, ephemeral=True)



    @app_commands.command(name="sticky_note", description=text("cmd.sticky_note.description"))
    @app_commands.describe(title=text("cmd.sticky_note.title"), content=text("cmd.sticky_note.content"))
    async def sticky_note(self, interaction: discord.Interaction, title: str, content: str):
        for i in events:
            if i["event"] == title:
                await interaction.response.send_message(text("cmd.sticky_note.exist"))
                return
        if len(content) >= 100:
            await interaction.response.send_message(text("cmd.sticky_note.word_limit",len(content)))
            return
        tar = {
            "note": 1,
            "year": datetime.datetime.now().year,
            "month": datetime.datetime.now().month,
            "day": datetime.datetime.now().day,
            "hour": datetime.datetime.now().hour,
            "minute": datetime.datetime.now().minute,
            "event": title,
            "content": content,
            "user": interaction.user.id
        }
        events.append(tar)
        sync_json()
        embed = discord.Embed(
            title=title,
            description=content,
            color=settings.Colors.notice
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="note_list", description=text("cmd.notice_list.description"))
    async def note_list(self, interaction: discord.Interaction):
        sticky_notes = []
        notice = discord.Embed(
            title=text("cmd.notice_list.title"),
            description="",
            color=settings.Colors.notice
        )
        have_sticky_notes = False
        have_notice = False
        for i in events:
            if interaction.user.id == i["user"]:
                if i["note"]:
                    embed = discord.Embed(
                        title=i["event"],
                        description=i["content"],
                        color=settings.Colors.notice
                    )
                    sticky_notes.append(embed)
                    have_sticky_notes = True
                else:
                    notice.add_field(name=i["event"], value=f"{i['year']}/{i['month']}/{i['day']} {pre_zero(i['hour'])}:{pre_zero(i['minute'])}", inline=False)
                    have_notice = True
        if have_sticky_notes:
            await interaction.response.send_message(content=text("cmd.notice_list.sticky_notes_below"), embeds=sticky_notes)
            if have_notice:
                await interaction.followup.send(content=text("cmd.notice_list.notice_below"), embed=notice)   
        elif have_notice:
            await interaction.response.send_message(content=text("cmd.notice_list.notice_below"), embed=notice)
        else:
            await interaction.response.send_message(content=text("cmd.notice_list.none"))



async def setup(bot):
    await bot.add_cog(Notice(bot))