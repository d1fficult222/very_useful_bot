import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
import os, json
import settings



    
class Options:
    def __init__(self, type: any, default: any):
        self.type = type
        self.default = default

def is_color(value: str) -> bool:
    if value[0] != "#":
        return False
    for i in value:
        if i not in "#0123456789abcdefABCDEF":
            return False
    return True



defaults = {
    "WordleBackgroundColor": Options("color", "#2E2E34"),
    "WordleBlockSize": Options("int", 50),
    "WordleBlockMargin": Options("int", 5),
    "WordleFontColor": Options("color", "#FFFFFF"),
    "WordleGrayColor": Options("color", "#3A3A3C"),
    "WordleGreenColor": Options("color", "#538D4E"),
    "WordleImageMargin": Options("int", 0),
    "WordleYellowColor": Options("color", "#B59F3B"),
    "CalendarBlockSize": Options("int", 50),
    "CalendarBlockMargin": Options("int", 5),
    "CalendarBackgroundColor": Options("color", "#23283b"),
    "CalendarColor1": Options("color", "#f7ca18"),
    "CalendarFontColor1": Options("color", "#e0e6ed")
                                       
}

def get_user_options(user_id: int, option_id: str) -> any:
    path = f"assets/user_options/{user_id}.json"
    if os.path.exists(path):
        with open(path, "r") as file:
            options = json.load(file)
        try:
            # return the key
            return options[option_id]
        except KeyError:
            # key not found
            return defaults[option_id].default
    else:
        # file does not exist
        return defaults[option_id].default
        



class UserOptions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("option")

    



    @app_commands.command(name="option", description="[選項] 變更個人指令選項")
    @app_commands.describe(key="key", value="value")
    @app_commands.choices(key = [Choice(name=i, value=i) for i in defaults.keys()])
    async def option(self, interaction: discord.Interaction, key: Choice[str], value: str):
        # Check if value is valid
        if key.value not in self.defaults.keys():
            await interaction.response.send_message(f"Key `{key.value}` 不存在")
            # raise ValueError(f"Key {key.value} does not exist.")
            return
        match self.defaults[key.value].type:
            case "color":
                if not self.is_color(value):
                    await interaction.response.send_message(f"`{value}` 的類別不是 `color`")
                    # raise ValueError(f"'{value}' is not a color, expected type is color.")
                    return
            case "int":
                try:
                    value = int(value)
                except Exception as e:
                    await interaction.response.send_message(f"`{value}` 的類別不是 `int`")
                    # raise ValueError(f"'{value}' is not an int, expected type is int. Error: {e}")
                    return
            case "str":
                # What could possibly go wrong?
                pass
        
        # Open file
        path = f"assets/user_options/{interaction.user.id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                options = json.load(f)
        else:
            options = {i: j.default for i, j in self.defaults.items()}

        # Change option
        options[key.value] = value

        # Write back file
        try:
            with open(path, "w") as f:
                f.write(json.dumps(options, indent=4))
        except FileNotFoundError:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(json.dumps(options, indent=4))

        # Output
        embed = discord.Embed(
            title="已變更選項",
            description=f"**`{key.value}`** 已設為 **`{value}`** (預設: `{self.defaults[key.value].default}`)",
            color=settings.Colors.success
        )
        await interaction.response.send_message(embed=embed)



async def setup(bot: commands.Bot):
    await bot.add_cog(UserOptions(bot))