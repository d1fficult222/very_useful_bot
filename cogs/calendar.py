import discord
from discord.ext import commands, tasks
from datetime import datetime
from lang import *
import calendar
from calendar_tools.calendar_tools import *
from navigator.navigator_utils import get_route, location_search
from pathlib import Path


class AddEventModal(discord.ui.Modal, title=text("calendar.add_event.title")):
    summary = discord.ui.TextInput(
        label=text("calendar.add_event.summary_label"),
        placeholder=text("calendar.add_event.summary_placeholder"),
        required=True,
        max_length=50
    )
    start_time = discord.ui.TextInput(
        label=text("calendar.add_event.start_time_label"),
        placeholder=text("calendar.add_event.start_time_placeholder"),
        required=True,
        min_length=16,
        max_length=16
    )
    location = discord.ui.TextInput(
        label=text("calendar.add_event.location_label"),
        placeholder=text("calendar.add_event.location_placeholder"),
        required=False,
        max_length=50
    )
    description = discord.ui.TextInput(
        label=text("calendar.add_event.description_label"),
        style=discord.TextStyle.paragraph,
        placeholder=text("calendar.add_event.description_placeholder"),
        required=False,
        max_length=300
    )
    notify_minutes = discord.ui.TextInput(
        label=text("calendar.add_event.notify_label"),
        placeholder=text("calendar.add_event.notify_placeholder"),
        required=False,
        max_length=5
    )

    def __init__(self, db, user_id: int = None):
        super().__init__()
        self.db = db
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            st_obj = datetime.strptime(self.start_time.value, "%Y-%m-%d %H:%M")
            # 自動設定結束時間為開始時間 + 30 分鐘
            from datetime import timedelta
            et_obj = st_obj + timedelta(minutes=30)
            
            st_str = st_obj.strftime("%Y-%m-%d %H:%M:%S")
            et_str = et_obj.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return await interaction.response.send_message(text("calendar.add_event.error.time_format"), ephemeral=True)

        # 處理提醒分鐘數
        notify_value = None
        
        # 如果有位置輸入，嘗試計算路線時間
        if self.location.value.strip():
            print(f"[AddEventModal] 使用者輸入位置：{self.location.value.strip()}")
            
            # 動態獲取 user_coords
            try:
                from cogs.navigator import user_coords as nav_user_coords
            except ImportError:
                nav_user_coords = {}
            
            user_location = nav_user_coords.get(str(interaction.user.id))
            print(f"[AddEventModal] 使用者位置座標：{user_location}")
            
            if user_location:
                try:
                    # 搜索目標位置
                    print(f"[AddEventModal] 開始搜索位置...")
                    search_results = location_search(
                        self.location.value.strip(),
                        center_coord={"lat": user_location["lat"], "lon": user_location["lon"]}
                    )
                    print(f"[AddEventModal] 搜索結果：{search_results}")
                    
                    if search_results and len(search_results) > 0:
                        first_result = search_results[0]
                        destination = {
                            "lat": float(first_result.get("lat")),
                            "lon": float(first_result.get("lon")),
                            "name": self.location.value.strip()
                        }
                        print(f"[AddEventModal] 目標位置：{destination}")
                        
                        # 計算路線 (預設使用步行)
                        print(f"[AddEventModal] 開始計算路線...")
                        BASE_DIR = Path(__file__).resolve().parent.parent
                        route_result = get_route(
                            {
                                "lat": user_location["lat"],
                                "lon": user_location["lon"],
                                "name": text("locations.your_location")
                            },
                            destination,
                            profile="foot",
                            output_path=BASE_DIR / "location_webpage" / "temp_route.html"
                        )
                        print(f"[AddEventModal] 路線結果：{route_result}")
                        
                        if route_result and "duration_minutes" in route_result:
                            # 使用路線時間作為提醒時間
                            notify_value = str(route_result["duration_minutes"])
                            print(f"[AddEventModal] 自動設置提醒時間為 {notify_value} 分鐘 (基於位置 {self.location.value.strip()})")
                        else:
                            # 路線計算失敗，按照原有邏輯處理
                            print(f"[AddEventModal] 路線計算失敗，回退到手動設置")
                            if self.notify_minutes.value.strip():
                                try:
                                    notify_value = str(int(self.notify_minutes.value.strip()))
                                except ValueError:
                                    return await interaction.response.send_message(text("calendar.add_event.error.invalid_notify"), ephemeral=True)
                            else:
                                notify_value = "0"
                    else:
                        # 搜索沒有結果，按照原有邏輯處理
                        print(f"[AddEventModal] 位置搜索沒有結果，回退到手動設置")
                        if self.notify_minutes.value.strip():
                            try:
                                notify_value = str(int(self.notify_minutes.value.strip()))
                            except ValueError:
                                return await interaction.response.send_message(text("calendar.add_event.error.invalid_notify"), ephemeral=True)
                        else:
                            notify_value = "0"
                except Exception as e:
                    print(f"[AddEventModal] 計算位置路線時發生錯誤: {e}")
                    import traceback
                    traceback.print_exc()
                    # 出錯時，按照原有邏輯處理
                    if self.notify_minutes.value.strip():
                        try:
                            notify_value = str(int(self.notify_minutes.value.strip()))
                        except ValueError:
                            return await interaction.response.send_message(text("calendar.add_event.error.invalid_notify"), ephemeral=True)
                    else:
                        notify_value = "0"
            else:
                # 用戶沒有位置信息，按照原有邏輯處理
                print(f"[AddEventModal] 使用者沒有位置信息，請先執行 /get_location 命令")
                if self.notify_minutes.value.strip():
                    try:
                        notify_value = str(int(self.notify_minutes.value.strip()))
                    except ValueError:
                        return await interaction.response.send_message(text("calendar.add_event.error.invalid_notify"), ephemeral=True)
                else:
                    notify_value = "0"
        else:
            # 沒有位置輸入，按照原有邏輯處理
            print(f"[AddEventModal] 沒有輸入位置")
            if self.notify_minutes.value.strip():
                try:
                    notify_value = str(int(self.notify_minutes.value.strip()))
                    print(f"[AddEventModal] {text('calendar.add_event.debug.notify_set', notify_value)}")
                except ValueError:
                    return await interaction.response.send_message(text("calendar.add_event.error.invalid_notify"), ephemeral=True)
            else:
                notify_value = "0"

        await self.db.add_event(
            summary=self.summary.value,
            description=self.description.value or None,
            location=self.location.value or None,
            participants=None,
            start_time=st_str,
            end_time=et_str,
            repeat=None,
            notify=notify_value,
            discord_user_id=interaction.user.id
        )
        
        notify_text = text("calendar.add_event.success.notify_before", notify_value) if notify_value != "0" else text("calendar.add_event.success.notify_instant")
        
        await interaction.response.send_message(
            f"{text('calendar.add_event.success.title', self.summary.value)}\n"
            f"{text('calendar.add_event.success.start_time', st_str)}\n"
            f"{text('calendar.add_event.success.end_time', et_str)}\n"
            f"{notify_text}", 
            ephemeral=True
        )

class DeleteEventView(discord.ui.View):
    def __init__(self, db, discord_user_id: int, events: list):
        super().__init__(timeout=60)
        self.db = db
        self.user_id = discord_user_id
        self.selected_event_id = None
        self.selected_event_summary = None

        options = []
        for event_id, summary, start_time in events[:25]:
            options.append(discord.SelectOption(
                label=summary,
                description=text("calendar.delete.select_option_time", start_time),
                value=str(event_id)
            ))

        self.select_menu = discord.ui.Select(
            placeholder=text("calendar.delete.select_placeholder"),
            min_values=1,
            max_values=1,
            options=options
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(text("calendar.error.cannot_operate_menu"), ephemeral=True)

        self.selected_event_id = int(self.select_menu.values[0])
        
        for option in self.select_menu.options:
            if option.value == self.select_menu.values[0]:
                self.selected_event_summary = option.label

        self.clear_items()
        
        confirm_btn = discord.ui.Button(label=text("calendar.button.confirm_delete"), style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label=text("calendar.button.cancel"), style=discord.ButtonStyle.secondary)
        
        confirm_btn.callback = self.confirm_callback
        cancel_btn.callback = self.cancel_callback
        
        self.add_item(confirm_btn)
        self.add_item(cancel_btn)

        await interaction.response.edit_message(
            content=text("calendar.delete.confirm_message", self.selected_event_summary),
            view=self
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(text("calendar.error.cannot_operate_button"), ephemeral=True)

        success = await self.db.delete_event(self.selected_event_id, self.user_id)
        
        self.clear_items()
        if success:
            await interaction.response.edit_message(content=text("calendar.delete.success", self.selected_event_summary), view=self)
        else:
            await interaction.response.edit_message(content=text("calendar.delete.error.failed"), view=self)
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(text("calendar.error.cannot_operate_button"), ephemeral=True)

        self.clear_items()
        await interaction.response.edit_message(content=text("calendar.delete.cancelled"), view=self)
        self.stop()

    async def on_timeout(self):
        self.clear_items()
        self.stop()

class CalendarView(discord.ui.View):
    def __init__(self, db, discord_user_id: int, year: int, month: int):
        super().__init__(timeout=180) # 3 分鐘後按鈕失效
        self.db = db
        self.user_id = discord_user_id
        self.year = year
        self.month = month

    def generate_calendar_text(self, events: list) -> str:
        """核心排版邏輯：將月曆矩陣轉為對齊的純文字"""
        month_matrix = calendar.monthcalendar(self.year, self.month)
        
        event_days = set()
        for _, start_time in events:
            try:
                dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                if dt.year == self.year and dt.month == self.month:
                    event_days.add(dt.day)
            except ValueError:
                continue

        calendar_text = " 一  二  三  四  五  六  日\n"
        calendar_text += "-------------------------\n"

        for row in month_matrix:
            row_text = ""
            for day in row:
                if day == 0:
                    row_text += "    "
                else:
                    mark = "+" if day in event_days else " "
                    row_text += f"{day:2d}{mark} "
            calendar_text += row_text + "\n"
            
        return f"```\n{calendar_text}```"

    async def update_message(self, interaction: discord.Interaction):
        """當月份改變時，重新撈取資料並更新 Embed 畫面"""
        events = await self.db.get_events_by_month(self.user_id, self.year, self.month)
        
        calendar_code_block = self.generate_calendar_text(events)
        
        embed = discord.Embed(
            title=text("calendar.view.calendar_title", self.year, self.month),
            description=calendar_code_block,
            color=discord.Color.green()
        )
        
        if events:
            event_list_text = ""
            for summary, start_time in events:
                short_time = start_time[8:16] 
                event_list_text += f"• `{short_time}` {summary}\n"
            embed.add_field(name=text("calendar.view.event_list_title"), value=event_list_text, inline=False)
        else:
            embed.add_field(name=text("calendar.view.event_list_title"), value=text("calendar.view.no_events"), inline=False)
            
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=text("calendar.button.prev_month"), style=discord.ButtonStyle.secondary)
    async def prev_month(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(text("calendar.error.cannot_operate_calendar"), ephemeral=True)
        
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
            
        await self.update_message(interaction)

    @discord.ui.button(label=text("calendar.button.next_month"), style=discord.ButtonStyle.secondary)
    async def next_month(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(text("calendar.error.cannot_operate_calendar"), ephemeral=True)
        
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
            
        await self.update_message(interaction)



class Calendar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = CalendarDB()

    async def cog_load(self):
        try:
            print("[日曆 Cog] 開始初始化資料庫...")
            await self.db.init_db()
            print("[日曆 Cog] ✅ 行事曆資料庫載入完成")
        except Exception as e:
            print(f"[日曆 Cog] 初始化資料庫失敗: {e}")
            
        try:
            print(f"[日曆 Cog] 檢查提醒循環狀態：is_running = {self.reminder_loop.is_running()}")
            if not self.reminder_loop.is_running():
                self.reminder_loop.start()
                print("[日曆 Cog] ✅ 提醒迴圈 (Task Loop) 已啟動！")
            else:
                print("[日曆 Cog] ⚠️ 提醒迴圈已在執行中")
        except Exception as e:
            print(f"[日曆 Cog] 啟動提醒循環失敗: {e}")

    def cog_unload(self):
        self.bot.remove_command("add_event")
        self.bot.remove_command("delete_event")
        self.bot.remove_command("calendar")
        self.reminder_loop.stop()

    @tasks.loop(minutes=1.0)
    async def reminder_loop(self):
        try:
            await self.bot.wait_until_ready()
            print("[提醒循環] 開始檢查待提醒事件...")
            
            events = await self.db.get_triggering_reminders()
            print(f"[提醒循環] 找到 {len(events)} 個待提醒事件")
            
            for event_id, summary, description, user_id, start_time in events:
                try:
                    print(f"[提醒循環] 準備發送提醒給使用者 {user_id}：{summary}")
                    user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                    if user:
                        try:
                            # DM
                            embed = discord.Embed(
                                title=f"🔔 行事曆提醒：{summary}",
                                description=description or "無詳細說明",
                                color=discord.Color.blue()
                            )
                            embed.add_field(name="開始時間", value=start_time, inline=False)
                            await user.send(embed=embed)
                            print(f"[提醒循環] ✅ 成功發送提醒給 {user_id}")
                            
                            # mark as nofitied，避免重複提醒
                            await self.db.mark_as_notified(event_id)
                            
                        except discord.Forbidden:
                            print(f"[提醒循環] 無法私訊使用者 {user_id}，可能他關閉了隱私設定。")
                        except Exception as e:
                            print(f"[提醒循環] 發送提醒時發生錯誤: {e}")
                    else:
                        print(f"[提醒循環] 找不到使用者 {user_id}")
                except Exception as e:
                    print(f"[提醒循環] 處理事件 {event_id} 時出錯: {e}")
        except Exception as e:
            print(f"[提醒循環] 提醒循環本身出錯: {e}")
    
    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        print("[提醒循環] 等待 bot 準備就緒...")
        await self.bot.wait_until_ready()
        print("[提醒循環] bot 已準備就緒，提醒循環即將開始")


    
    @commands.hybrid_command(name="delete_event", description=text("calendar.command.delete_event.description"))
    async def delete_event_cmd(self, ctx):
        events = await self.db.get_upcoming_events(ctx.author.id)
        
        if not events:
            return await ctx.send(text("calendar.command.delete_event.no_events"))

        view = DeleteEventView(db=self.db, discord_user_id=ctx.author.id, events=events)
        
        await ctx.send(text("calendar.command.delete_event.select_prompt"), view=view)


    @commands.hybrid_command(name="add_event", description=text("calendar.command.add_event.description"))
    async def add_event_cmd(self, ctx: commands.Context):
        if ctx.interaction:
            modal = AddEventModal(db=self.db, user_id=ctx.author.id)
            await ctx.interaction.response.send_modal(modal)
        else:
            await ctx.send(text("calendar.command.add_event.error.form_only"))


    @commands.hybrid_command(name="calendar", description=text("calendar.command.calendar.description"))
    async def show_calendar_cmd(self, ctx):
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        events = await self.db.get_events_by_month(ctx.author.id, current_year, current_month)
        
        view = CalendarView(db=self.db, discord_user_id=ctx.author.id, year=current_year, month=current_month)
        
        calendar_code_block = view.generate_calendar_text(events)
        
        embed = discord.Embed(
            title=text("calendar.view.calendar_title", current_year, current_month),
            description=calendar_code_block,
            color=discord.Color.green()
        )
        
        if events:
            event_list_text = ""
            for summary, start_time in events:
                short_time = start_time[8:16]
                event_list_text += f"• `{short_time}` {summary}\n"
            embed.add_field(name=text("calendar.view.event_list_title"), value=event_list_text, inline=False)
        else:
            embed.add_field(name=text("calendar.view.event_list_title"), value=text("calendar.view.no_events"), inline=False)
            
        await ctx.send(embed=embed, view=view)



async def setup(bot: commands.Bot):
    cog = Calendar(bot)
    await bot.add_cog(cog)
    print("[日曆 Setup] Calendar cog 已添加到 bot")
    # 確保 cog_load 被調用
    await cog.cog_load()
    print("[日曆 Setup] Calendar cog 初始化完成")