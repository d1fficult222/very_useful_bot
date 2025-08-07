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
    


# Easter eggs
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "hello world":
        await message.channel.send(text("bot.helloworld"))



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



# Run the bot
bot.run(token)