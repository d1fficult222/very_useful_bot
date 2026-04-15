import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

import settings
from lang import text




# Token
load_dotenv()
token = os.getenv("TOKEN")
if not token:
    print(text("bot.token_notfound"))
    exit()
                


# Create bot instance
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())


# Load bot
@bot.event
async def on_ready():
    # Load cogs
    loaded_commands = 0
    loaded_failed = 0
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(text("bot.cog_loaded", filename))
                loaded_commands += 1
            except Exception as e:
                print(text("bot.cog_load_error", filename, e))
                loaded_failed += 1
    print(text("bot.cogs_load_count", loaded_commands, loaded_failed))
    # Sync Commands
    try:
        synced = await bot.tree.sync()
        print(text("bot.commands_synced", len(synced)))
    except Exception as e:
        print(text("bot.commands_sync_error", e))
    # Logged in successfully
    print(text("bot.login", bot.user.name))
    # Set bot status
    match settings.Activity.doing:
        case "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=settings.Activity.content)
            await bot.change_presence(activity=activity)
        case "playing":
            activity = discord.Game(name=settings.Activity.content)
            await bot.change_presence(activity=activity)
        case "listening":
            activity = activity=discord.Activity(type=discord.ActivityType.listening, name=settings.Activity.content)
            await bot.change_presence(activity=activity)
        case _:
            pass
    


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Hello world
    if message.content == "hello world":
        await message.channel.send(text("bot.helloworld"))
    # Save DM messages and DM to admin
    if isinstance(message.channel, discord.DMChannel):
        view = DMConfirmView(message)
        sent_message = await message.channel.send("您想將此訊息傳送給 VeryUsefulBot 維護人員嗎?", view=view)
        view.message = sent_message
    await bot.process_commands(message)



class DMConfirmView(discord.ui.View):
    def __init__(self, message):
        super().__init__(timeout=60)
        self.original_message = message
        self.message = None

    @discord.ui.button(label="是", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_id = 1011979714283454586
        admin = bot.get_user(admin_id)
        if admin:
            await admin.send(f"來自 {self.original_message.author} 的訊息: {self.original_message.content}")
            await interaction.response.send_message("訊息已傳送給維護人員", ephemeral=True)
        else:
            await interaction.response.send_message("發生錯誤：無法找到維護人員，請聯絡維護人員。", ephemeral=True)
        # 刪除按鈕
        await self.message.edit(view=None)

    @discord.ui.button(label="否", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("未傳送訊息", ephemeral=True)
        # Disable 按鈕
        self.yes.disabled = True
        self.no.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        # Disable 按鈕
        self.yes.disabled = True
        self.no.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass



# Load and unload commands
class EnterPswView(discord.ui.Modal, title=text("bot.enterpsw.title")):
    def __init__(self, do: str, extension: str):
        super().__init__()
        self.do = do
        self.extension = extension
    
    password_box = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label=text("bot.enterpsw"),
        required=True,
        placeholder=text("bot.enterpsw.placeholder")
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        password = os.getenv("PASSWORD")
        if password is None:
            await interaction.response.send_message(text("bot.warning.no_psw"), ephemeral=True)
        elif password != self.password_box.value:
            await interaction.response.send_message(text("bot.incorrect_psw"),ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)

        try:
            match self.do:
                case "load":
                    await bot.load_extension(f"cogs.{self.extension}")
                    synced = await bot.tree.sync()
                    await interaction.followup.send(f"{text('cmd.load.loaded', self.extension)}\n{text('bot.commands_synced', len(synced))}")
                case "unload":
                    await bot.unload_extension(f"cogs.{self.extension}")
                    synced = await bot.tree.sync()
                    await interaction.followup.send(f"{text('cmd.unload.unloaded', self.extension)}\n{text('bot.commands_synced', len(synced))}")
                case "reload":
                    await bot.reload_extension(f"cogs.{self.extension}")
                    synced = await bot.tree.sync()
                    await interaction.followup.send(f"{text('cmd.reload.reloaded', self.extension)}\n{text('bot.commands_synced', len(synced))}")
        except Exception as e:
            await interaction.followup.send(text(f"cmd.{self.do}.error", self.extension, e))




@bot.hybrid_command(name="load", description=text("cmd.load.description"))
async def load(ctx: commands.Context, extension: str):
    await ctx.interaction.response.send_modal(EnterPswView(do="load", extension=extension))

@bot.hybrid_command(name="unload", description=text("cmd.unload.description"))
async def unload(ctx: commands.Context, extension: str):
    await ctx.interaction.response.send_modal(EnterPswView(do="unload", extension=extension))

@bot.hybrid_command(name="reload", description=text("cmd.reload.description"))
async def reload(ctx: commands.Context, extension: str):
    await ctx.interaction.response.send_modal(EnterPswView(do="reload", extension=extension))

@bot.hybrid_command(name="senddm", description="將指定內容私訊給指定使用者（需提供密碼）")
async def senddm(ctx: commands.Context, message: str, user_id: int, password: str):
    """私訊指定 user_id（數字），需提供正確密碼才能發送。"""

    expected = os.getenv("PASSWORD")
    if expected is None:
        await ctx.interaction.response.send_message("伺服器尚未設定 PASSWORD，無法進行驗證。", ephemeral=True)
        return

    if password != expected:
        await ctx.interaction.response.send_message("密碼錯誤，無法發送私訊。", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(user_id)
        await user.send(message)
        await ctx.interaction.response.send_message(f"已傳送訊息給 <@{user_id}>。", ephemeral=True)
    except Exception as e:
        await ctx.interaction.response.send_message(f"無法傳送私訊：{e}", ephemeral=True)

@bot.hybrid_command(name="about", description=text("bot.about"))
async def about(ctx: commands.Context):
    embed = discord.Embed(
        title="{} {}".format(text("bot.name"), settings.Version),
        description=text("bot.description"),
        color=settings.Colors.success
    )
    await ctx.interaction.response.send_message(embed=embed)

# Run the bot
bot.run(token)