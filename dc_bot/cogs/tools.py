import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from discord.ui import Button, View
import datetime
import settings
from lang import *





class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("calculator")





    class CalculatorView(View):
        def __init__(self):
            super().__init__()
            self.screen: str = "0"

            buttons = [
                ["(", ")", text("calculator.backspace"), text("calculator.clear_all")],# Row 1
                ["7", "8", "9", "÷"],  # Row 2
                ["4", "5", "6", "×"],  # Row 3
                ["1", "2", "3", "-"],  # Row 4
                ["0", ".", "=", "+"]   # Row 5
            ]
            styles = [
                [discord.ButtonStyle.primary, discord.ButtonStyle.primary, discord.ButtonStyle.primary, discord.ButtonStyle.danger],
                [discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.primary],
                [discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.primary],
                [discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.primary],
                [discord.ButtonStyle.secondary, discord.ButtonStyle.secondary, discord.ButtonStyle.success, discord.ButtonStyle.primary],
            ]
            for i in range(len(buttons)):
                for j in range(len(buttons[i])):
                    button = Button(label=buttons[i][j], style=styles[i][j], row=i,custom_id=buttons[i][j])
                    button.callback = self.button_callback
                    self.add_item(button)
            
        async def button_callback(self, interaction: discord.Interaction):
            button = interaction.data["custom_id"]

            if button == text("calculator.clear_all"):
                self.screen = "0"
            elif button == text("calculator.backspace"):
                self.screen = self.screen[0:len(self.screen)-1]
                if self.screen == '': self.screen = '0'
            elif button == "=":
                result = self.screen.replace("×", "*").replace("÷", "/").replace("%", "*0.01")
                try:
                    result = eval(result)
                except ZeroDivisionError:
                    embed = discord.Embed(
                        title=text("calculator.banned", interaction.user.name),
                        description=text("calculator.banned_reason"),
                        color=settings.Colors.fail
                    )
                    global blacklist
                    blacklist.append(interaction.user.name)
                    with open("assets/calculator_blacklist.txt", "w") as file:
                        for item in blacklist:
                            file.write(f"{item}\n")
                    await interaction.message.delete()
                    await interaction.response.send_message(embed=embed)
                    return
                except Exception as e:
                    result = e
                self.screen = '0'
                await self.update_calculator(interaction, result)
                return

            else:
                if button == '.' and (self.screen[len(self.screen)-1] not in ['1','2','3','4','5','6','7','8','9']):
                    self.screen += "0."
                elif self.screen == '0' and (button not in ['+', '-', '×', '÷', '%']):
                    self.screen = button
                else:
                    self.screen += button
            await self.update_calculator(interaction)



        async def update_calculator(self, interaction: discord.Interaction, *args):
            embed = discord.Embed(
                title="",
                description=f"# ```{self.screen}```",
                color=settings.Colors.math
            )
            if args:
                embed.description = f"# ```{args[0]}```"
            await interaction.response.edit_message(embed=embed, view=self)



    @app_commands.command(name="calculator", description=text("cmd.calculator.description"))
    async def calculator(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="",
            description=f"# ```0```",
            color=settings.Colors.math
        )
        await interaction.response.send_message(embed=embed, view=self.CalculatorView())





@app_commands.context_menu(name=text("menu.evaluate"))
async def calculate(interaction: discord.Interaction, message: discord.Message):
    to_calculate = message.content
    to_calculate = to_calculate.replace(" ", "")
    to_calculate = to_calculate.rstrip("=")
    try:
        result = eval(to_calculate)
        await interaction.response.send_message(f"{to_calculate} = **{result}**")
    except Exception as e:
        await interaction.response.send_message(text("menu.evaluate.fail", e))





class Daysleft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("daysleft")

    # Check if it's a leap year
    def is_leap(year: int) -> bool:
        if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
            return True
        else:
            return False


    # Check if a date if valid
    def is_vaild_date(self, year: int, month: int, date: int) -> bool:
        if (date not in range(1,32)) or (month not in range(1,13)) or (year < 1):
            return False
        if month in [4,6,9,11] and date == 31:
            return False
        if month == 2 and date > 28:
            if self.is_leap(year) and date <= 29:
                return True
            else:
                return False
        else:
            return True


    @app_commands.command(name="daysleft", description=text("cmd.daysleft.description"))
    @app_commands.describe(
        year=text("cmd.daysleft.year"),
        month=text("cmd.daysleft.month"),
        date=text("cmd.daysleft.date"),
        add=text("cmd.daysleft.add")
    )
    @app_commands.choices(
        add = [
            Choice(name=text("cmd.daysleft.yes"), value=1),
            Choice(name=text("cmd.daysleft.no"), value=0)
        ]
    )
    async def daysleft(
        self, 
        interaction: discord.Interaction,
        year: app_commands.Range[int,2024,2099],
        month: app_commands.Range[int,1,12],
        date: app_commands.Range[int,1,31],
        add: Choice[int]
    ):
        if not self.is_vaild_date(year, month, date):
            await interaction.response.send_message(text("cmd.daysleft.not_valid",year,month,date))
        else:
            target = datetime.datetime(year, month, date)
            today = datetime.datetime.now()

            days_left = (target - today).days + 1
            if add.value: days_left += 1

            embed = discord.Embed(
                title=text("cmd.daysleft.left", days_left),
                description=text("cmd.daysleft.target",year,month,date),
                timestamp=datetime.datetime.now()
            )
            if add.value:
                title += text("cmd.daysleft.included")
            await interaction.response.send_message(embed=embed)




@app_commands.context_menu(name=text("menu.wordcount"))
async def wordcount(interaction: discord.Interaction, message: discord.Message):
    try:
        word = str(message.content)
        embed = discord.Embed(
            title=text("menu.wordcount.title"),
            description="",
            color=settings.Colors.success
        )
        embed.add_field(name=text("menu.wordcount.words"), value=len(word.split(" ")))
        embed.add_field(name=text("menu.wordcount.chars"), value=len(word))
        embed.add_field(name=text("menu.wordcount.chars_no_space"), value=len(word.replace(" ", "")))
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(text("menu.wordcount,err"),e)




class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("ping")

    
    @app_commands.command(name="ping", description=text("cmd.ping.description"))
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # s to ms
        await interaction.response.send_message(text("cmd.ping.latency", latency))





async def setup(bot: commands.Bot):
    await bot.add_cog(Calculator(bot))
    await bot.add_cog(Daysleft(bot))
    await bot.add_cog(Ping(bot))
    bot.tree.add_command(calculate)
    bot.tree.add_command(wordcount)