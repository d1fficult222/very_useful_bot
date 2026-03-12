import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, button, View
from lang import *
import settings
import random, asyncio

class SlotMachine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("slot")

    class PlayAgain(View):
        def __init__(self, cog):
            super().__init__()
            self.cog = cog
        
        @button(label=text('cmd.slot.again'), style=discord.ButtonStyle.green)
        async def play_again(self, interaction: discord.Interaction, button: Button):
            button.disabled = True
            await interaction.message.edit(view=self)
            await interaction.response.defer()
            await self.cog.run_slot(interaction=interaction, replay=True)

    async def run_slot(self, interaction: discord.Interaction, replay: bool):
        WAIT = 0.1
        items = ["🍒","7️⃣","🍋","🔔","🍇"]
        slot = random.sample(range(len(items)-1), 3)
        hold = [False, False, False]
        def slot_display() -> str:
            return f"""
            # ⬛ {'🔻' if hold[0] else '⬛'} {'🔻' if hold[1] else '⬛'} {'🔻' if hold[2] else '⬛'} ⬛\n
            # ⬛ {items[slot[0]]} {items[slot[1]]} {items[slot[2]]} ⬛\n
            # ⬛ {'🔺' if hold[0] else '⬛'} {'🔺' if hold[1] else '⬛'} {'🔺' if hold[2] else '⬛'} ⬛
            """
        # embed
        embed = discord.Embed(
            title=text("cmd.slot.title"),
            description=slot_display(),
            color=settings.Colors.wordle
        )
        if not replay:
            await interaction.response.send_message(embed=embed)
        OG_MESSAGE = await interaction.original_response()
        
        # Spin all three
        for i in range(random.randint(10,15)):
            slot[0] = slot[0]+1 if slot[0] != len(items)-1 else 0
            slot[1] = slot[1]+1 if slot[1] != len(items)-1 else 0
            slot[2] = slot[2]+1 if slot[2] != len(items)-1 else 0
            embed.description = slot_display()
            await OG_MESSAGE.edit(embed=embed)
            await asyncio.sleep(WAIT)
        
        # Hold 0
        hold[0] = True
        for i in range(random.randint(5,8)):
            slot[1] = slot[1]+1 if slot[1] != len(items)-1 else 0
            slot[2] = slot[2]+1 if slot[2] != len(items)-1 else 0
            embed.description = slot_display()
            await OG_MESSAGE.edit(embed=embed)
            await asyncio.sleep(WAIT)
        
        # Hold 1
        hold[1] = True
        for i in range(random.randint(5,8)):
            slot[2] = slot[2]+1 if slot[2] != len(items)-1 else 0
            embed.description = slot_display()
            await OG_MESSAGE.edit(embed=embed)
            await asyncio.sleep(WAIT)
        
        # Hold 2
        hold[2] = True
        embed.description = slot_display()
        await OG_MESSAGE.edit(embed=embed)
        await asyncio.sleep(WAIT)

        # Money
        if slot[0] == slot[1] and slot[1] == slot[2]:
            embed.description += f"\n {text('cmd.slot.jackpot')}"
            embed.add_field(name=text("cmd.slot.win"), value="+1000")
            await OG_MESSAGE.edit(embed=embed, view=self.PlayAgain(self))
        elif slot[0] == slot[1] or slot[1] == slot[2] or slot[2] == slot[0]:
            embed.description += f"\n {text('cmd.slot.win_two')}"
            embed.add_field(name=text("cmd.slot.win"), value="+200")
            await OG_MESSAGE.edit(embed=embed, view=self.PlayAgain(self))
        else:
            embed.description += f"\n {text('cmd.slot.lose')}"
            await OG_MESSAGE.edit(embed=embed, view=self.PlayAgain(self))

    @app_commands.command(name="slot", description=text("cmd.slot.description"))
    async def slot(self, interaction: discord.Interaction):
        await self.run_slot(interaction=interaction, replay=False)




async def setup(bot: commands.Bot):
    await bot.add_cog(SlotMachine(bot))