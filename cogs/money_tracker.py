import discord
from discord import app_commands
from discord.ext import commands
import os, json, datetime
import settings
from discord.app_commands import Choice, Range
from lang import *

class MoneyTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("m_wallet")
        self.bot.remove_command("m_new_record")



    
    def get_user_wallet(self, user_id: int) -> dict:
        path = f"assets/expenses/{user_id}.json"
        if os.path.exists(path):
            with open(path, 'r', encoding="utf-8") as f:
                return json.load(f)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding="utf-8") as f:
                user_wallet = {
                    "name": user_id,
                    "balance": 0,
                    "history": [{
                        "date": datetime.datetime.now().strftime("%Y%m%d_%H%M"),  # YYYYMMDD
                        "amount": 0,
                        "category": text("expenses.categories.other_income"),
                        "description": text("expenses.initialize"),
                        "balance": 0
                    }]
                }
                f.write(json.dumps(user_wallet, indent=4, ensure_ascii=False))
            return user_wallet


    def gen_table(self, header: list, width: list, *items: list) -> str:
        """
        Generates a formatted table as a string.
        """

        def setw(word: str, length: int, use_spacer: bool) -> str:
            word = str(word)
            if len((word)) < length:
                my_word = ""
                for i in range(len(word)):
                    my_word += word[i]
                for i in range(length - len(word)):
                    my_word += text("passbook.spacer") if use_spacer else " "
                return my_word
            else:
                my_word = ""
                for i in range(length):
                    my_word += word[i]
                return my_word
        
        table = ""

        for i in range(len(header)):
            table += setw(header[i], width[i], False if i >= 3 else True) + text("passbook.spacer")
        table += "\n\n"

        for i in items:
            if len(i) != len(width):
                raise ValueError("Row length in items does not match the width list length.")
            for j in range(len(i)):
                table += setw(i[j], width[j], False if j >= 3 else True) + text("passbook.spacer")
            table += "\n"
        
        return table

    income_categories = [
        text("expenses.categories.main_income"),
        text("expenses.categories.side_job"),
        text("expenses.categories.investment"),
        text("expenses.categories.other_income")
    ]
    expense_categories = [
        text("expenses.categories.monthly_expenses"),
        text("expenses.categories.food"),
        text("expenses.categories.transportation"),
        text("expenses.categories.entertainment"),
        text("expenses.categories.education"),
        text("expenses.categories.donation"),
        text("expenses.categories.lend"),
        text("expenses.categories.other_expenses")
    ]


    @app_commands.command(name="m_wallet", description=text("cmd.m_wallet.description"))
    async def m_wallet(self, interaction: discord.Interaction):
        user_wallet = self.get_user_wallet(interaction.user.id)

        user_history = user_wallet["history"]
        
        # flip the order of the list
        history = [{}] * len(user_history)
        for i in range(len(user_history)):
            history[len(user_history)-1-i] = user_history[i]

        # this month only
        this_month_history= []
        for i in range(len(history) if len(history) < 20 else 20):
            if history[i]["date"][:6] == datetime.datetime.now().strftime("%Y%m"):  # YYYYMM
                this_month_history.append(history[i])
        
        # the table 
        headers = [text("passbook.date"), text("passbook.category"), text("passbook.description"), text('passbook.withdraws'), text('passbook.deposit'), text('passbook.balance')]
        rows = [[i['date'][4:8], i['category'], i['description'], i['amount']*-1 if i['amount'] <= 0 else '', i['amount'] if i['amount'] > 0 else '', i['balance']] for i in this_month_history]
        passbook = f"```{self.gen_table(headers, [4,2,10,5,5,5], *rows)}```"

        embed = discord.Embed(
            title=text("cmd.m_wallet.someones_wallet", interaction.user.name),
            description=text("cmd.m_wallet.your_balance", user_wallet['balance']),
            color=settings.Colors.money,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(passbook, embed=embed, ephemeral=True)


    @app_commands.command(name="m_new_record", description=text("cmd.m_new_record.description"))
    @app_commands.describe(amount=text("cmd.m_new_record.amount"), category=text("cmd.m_new_record.category"), description=text("cmd.m_new_record.des"))
    @app_commands.choices(category = [Choice(name=text("cmd.m_new_record.income", i), value='0'+i) for i in income_categories] + [Choice(name=text("cmd.m_new_record.expense", i), value='1'+i) for i in expense_categories])
    async def m_new_record(self, interaction: discord.Interaction, amount: Range[int, 1, None], category: Choice[str], description: str):
        # get user wallet
        user_wallet = self.get_user_wallet(interaction.user.id)
        # income or expense
        if amount < 0: amount = amount * -1
        amount = amount * -1 if category.value[0] == '1' else amount
        # transaction
        this = {
            "date": datetime.datetime.now().strftime("%Y%m%d_%H%M"),
            "amount": amount,
            "category": category.value[1:],
            "description": description,
            "balance": user_wallet['balance'] + amount
        }
        user_wallet['history'].append(this)
        user_wallet['balance'] = this['balance']
        # sync to json file
        with open(f"assets/expenses/{interaction.user.id}.json", 'w', encoding="utf-8") as f:
            f.write(json.dumps(user_wallet, indent=4, ensure_ascii=False))
        # embed
        embed = discord.Embed(
            title=f"+ {this['amount']}" if this['amount']>0 else this['amount'],
            description=this['description'],
            color=settings.Colors.money,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name=text("cmd.m_new_record.category"), value=this["category"])
        embed.add_field(name=text("cmd.m_new_record.balance"), value=this["balance"])
        
        await interaction.response.send_message(embed=embed, ephemeral=True)




async def setup(bot: commands.Bot):
    await bot.add_cog(MoneyTracker(bot))
