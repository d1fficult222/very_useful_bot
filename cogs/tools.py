import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional
from lang import *


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("random")
        self.bot.remove_command("dice")


    @app_commands.command(name="random", description=text("random.description"))
    async def rand(self, interaction: discord.Interaction):
          
        class RandomWindow(discord.ui.Modal, title=text("random.window_title")):
            items = discord.ui.TextInput(
                label=text("random.items"),
                style=discord.TextStyle.paragraph,
                placeholder=text("random.items.placeholder"),
                required=True,
                max_length=1500,
            )
            amount = discord.ui.TextInput(
                label=text("random.amount"),
                style=discord.TextStyle.short,
                placeholder=text("random.amount.placeholder"),
                required=False
            )

            async def on_submit(self, interaction: discord.Interaction):
                items = self.items.value.split("\n")
                if not self.amount.value:
                    amount = 1
                else:
                    try:
                        amount = int(self.amount.value)
                        if amount < 0 or amount > len(items): amount = 1
                    except ValueError:
                        amount = 1
                
                embed = discord.Embed(title=text("random.result"))
                embed.add_field(name=text("random.amount"), value=amount)
                embed.add_field(name=text("random.items"), value=str(items).replace('[','').replace(']','').replace("'",''))

                if amount == 1:
                    selected = random.choice(items)
                    embed.description = f"## {selected}"
                else:
                    selected = random.sample(items, amount)
                    embed.description = "\n".join([f"## - **{i}**" for i in selected])
                
                await interaction.response.send_message(embed=embed)

        await interaction.response.send_modal(RandomWindow())


    @commands.hybrid_command(name="dice", description=text("dice.desription"))
    @discord.app_commands.describe(faces=text("dice.faces"), amount=text("dice.amount"))
    async def dice(self, ctx: commands.Context, faces: Optional[int], amount: Optional[int]):
        if faces is None:
            faces = 6
        if amount is None:
            amount = 1

        if faces < 1:
            faces = 1
        if amount < 1:
            amount = 1

        class DiceView(discord.ui.View):
            def __init__(self, author: discord.User, faces: int, amount: int):
                super().__init__()
                self.author = author
                self.faces = faces
                self.amount = amount

            def roll(self):
                if self.amount == 1:
                    return random.randint(1, self.faces)
                return [random.randint(1, self.faces) for _ in range(self.amount)]

            def format_result(self, result):
                if isinstance(result, list):
                    return ", ".join(str(v) for v in result)
                return str(result)

            async def update_message(self, interaction: discord.Interaction):
                result = self.roll()
                content = text("dice.result", self.format_result(result))
                await interaction.response.edit_message(content=content, view=self)

            async def on_timeout(self):
                if not self.message:
                    return
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                try:
                    await self.message.edit(view=self)
                except discord.HTTPException:
                    pass

            @discord.ui.button(label=text("dice.again"), style=discord.ButtonStyle.primary)
            async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.author:
                    await interaction.response.send_message(text("dice.wrong_author"), ephemeral=True)
                    return
                await self.update_message(interaction)

        view = DiceView(ctx.author, faces, amount)
        result = view.roll()
        content = text("dice.result", view.format_result(result))
        await ctx.send(content, view=view)








async def setup(bot: commands.Bot):
    await bot.add_cog(Tools(bot))