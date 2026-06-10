import aiosqlite
from datetime import datetime
from lang import *

class CalendarDB:
    def __init__(self, db_path: str = "assets/calendar_bot.db"):
        self.db_path = db_path


    async def init_db(self):
        """
        建立行事曆 Database
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,              -- 標題 (str)
                description TEXT,                   -- 說明 (str)
                location TEXT,                      -- 地點名稱 (str)
                latitude FLOAT,                     -- 緯度 (float)
                longitude FLOAT,                    -- 經度 (float)
                participants TEXT,                  -- 參與者 (str)
                start_time TEXT NOT NULL,           -- 開始時間 ISO 8601 (str)
                end_time TEXT NOT NULL,             -- 結束時間 ISO 8601 (str)
                repeat TEXT,                        -- 重複 (str)
                notify TEXT,                        -- 提前提醒 (str)
                is_notified BOOLEAN DEFAULT 0,       -- 是否已提醒過 (bool)
                discord_user_id INTEGER NOT NULL,   -- Discord user ID (int)
                google_sync BOOLEAN DEFAULT 0       -- Sync to Gcalendar (bool)
            )
            ''')
            await db.commit()


    async def add_event(
        self,
        summary: str,
        description: str | None,
        location: str | None,
        participants: str | None,
        start_time: str,
        end_time: str,
        repeat: str | None,
        notify: str | None,
        discord_user_id: int
    ):
        """
        將一事件加入行事曆 Database
        """
        sql = '''INSERT INTO events (summary, description, location, participants, start_time, end_time, repeat, notify, discord_user_id)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(sql, (summary, description, location, participants, start_time, end_time, repeat, notify, discord_user_id))
            await db.commit()
        
        print(text("calendar.event.success", summary))


    async def get_upcoming_events(self, discord_user_id: int):
        """
        取得特定 Discord 使用者之後的所有未來行程
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
            SELECT summary, start_time, end_time, location 
            FROM events 
            WHERE start_time >= ? AND discord_user_id = ? 
            ORDER BY start_time ASC
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql, (now, discord_user_id)) as cursor:
                return await cursor.fetchall()
            

    async def get_triggering_reminders(self):
        """
        找出所有應該發送提醒的事件（當前時間 >= start_time - notify 分鐘，或預設在 start_time 時）
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
            SELECT id, summary, description, discord_user_id, start_time 
            FROM events 
            WHERE is_notified = 0 
              AND datetime(start_time, '-' || COALESCE(notify, '0') || ' minutes') <= ?
        """
        # start_time - notify (minutes)，notify 為 null 時預設為 0
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql, (now,)) as cursor:
                return await cursor.fetchall()


    async def mark_as_notified(self, event_id: int):
        """
        將事件標記為已提醒，避免重複發送
        """
        sql = "UPDATE events SET is_notified = 1 WHERE id = ?"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(sql, (event_id,))
            await db.commit()

        
    async def delete_event(self, event_id: int, discord_user_id: int) -> bool:
        """
        刪除特定使用者的特定行程
        """
        sql = "DELETE FROM events WHERE id = ? AND discord_user_id = ?"
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql, (event_id, discord_user_id)) as cursor:
                await db.commit()
                return cursor.rowcount > 0
            
    async def get_events_by_month(self, discord_user_id: int, year: int, month: int):
        """
        取得特定使用者在特定年份與月份的所有行程
        """
        start_date = f"{year}-{month:02d}-01 00:00:00"
        end_date = f"{year}-{month:02d}-31 23:59:59"
        
        sql = """
            SELECT summary, start_time 
            FROM events 
            WHERE discord_user_id = ? 
              AND start_time BETWEEN ? AND ?
            ORDER BY start_time ASC
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql, (discord_user_id, start_date, end_date)) as cursor:
                return await cursor.fetchall()
            
    