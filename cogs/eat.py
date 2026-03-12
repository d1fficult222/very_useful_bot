import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Range
import random
from typing import Optional
from lang import *





class Eat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("eat")



    

    @app_commands.command(name="eat", description=text("cmd.eat.description"))
    @app_commands.describe(amount=text("cmd.amount"))
    async def eat(self, interaction: discord.Interaction, amount: Optional[Range[int, 1, 30]]):
        with open("assets/foodlist.txt","r",encoding="UTF-8") as f:
            contents = f.readlines()
            foodlist = [i.strip() for i in contents]
        if not amount: amount = 1
        selected = []
        if len(foodlist) < amount:
            amount = len(foodlist)
        selected = random.sample(foodlist, amount)
        output = str(selected)
        output = output[1:len(output)-1]
        output = output.replace("'", "")
        output = output.replace(" ", "")
        output = output.replace(",", "、")
        j = random.randint(0, len(text("eat.prefix"))-1)
        await interaction.response.send_message(f"{text('eat.prefix')[j]} **{output}** {text('eat.ends')[j]}")





async def setup(bot: commands.Bot):
    await bot.add_cog(Eat(bot))