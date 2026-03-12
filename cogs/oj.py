import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Optional
import json, os, subprocess, random
import settings
from lang import *

class OJ(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("code")
        self.bot.remove_command("submit_code")
    



    def diffToName(self, difficulty: int) -> str: 
        match difficulty:
            case 0: return text("oj.easy")
            case 1: return text("oj.normal")
            case 2: return text("oj.hard")



    class SubmitWindow(discord.ui.Modal, title=text("oj.submit")):
        def __init__(self, cog):
            self.cog = cog

        codes = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            label=text("oj.insert"),
            required=True,
            placeholder=text("oj.placeholder")
        )

        async def on_submit(self, interaction: discord.Interaction):
            # load the data about this test
            global id_global #[difficulty, id]
            with open(f"assets/code_test/{id_global[0]}/{id_global[1]}.json", "r") as file:
                question = json.load(file)
            
            # prepare for discord embed
            embed = discord.Embed(
                title=f"{self.cog.diffToName(difficulty=id_global[0])} #{id_global[1]}",
                description="",
                color=settings.Colors.oj
            )
            
            # save the code
            global lang
            codes = self.codes.value
            with open(f"assets/run_code/test.{lang}", "w") as file:
                file.write(codes)

            # interaction must be sent within 3 seconds, so we need this
            await interaction.response.defer(thinking=True)

            # compile the code
            result = subprocess.run(["bash", f"assets/run_code/compile_{lang}.sh"], capture_output=True, text=True)
            if result.stderr:
                # An error occurred
                embed.title = text("oj.compilation_err")
                embed.description = result.stderr
                embed.color = settings.Colors.fail
                await interaction.followup.send(embed=embed)
                return

            # run code for every test data
            amount = len(question["tests"])
            passed = 0               # passed count
            errors = ["0"]*amount    # wrong output
            for i in range(amount):
                # load input data
                with open("assets/run_code/input.txt", "w") as file:
                    file.write(question["tests"][i]["input"])
                # let's run it
                runcode_path = f"assets/run_code/run_{lang}.sh"
                result = subprocess.run(["bash", runcode_path], capture_output=True, text=True)
                # check the result
                if result.stderr:
                    # An error occurred
                    embed.description = text("oj.error")
                    embed.add_field(name=text("oj.test_n_err:",i+1), value=result.stderr)
                    await interaction.followup.send(embed=embed)
                    return
                else:
                    if result.stdout.split() == question["tests"][i]["output"].split():
                        # Correct
                        passed += 1
                    else:
                        # Wrong
                        errors[i] = result.stdout
            
            # send the results to the user
            embed.description = text("oj.passed_txt",passed,amount)
            for i in range(amount):
                if errors[i] == "0":
                    embed.description += text("oj.test_n_passed",i+1)
                else:
                    embed.description += text("oj.test_n_failed",i+1)
                    embed.add_field(name=text("oj.test_n_input",i+1), value=question["tests"][i]["input"])
                    embed.add_field(name=text("oj.test_n_expected",i+1), value=question["tests"][i]["output"])
                    embed.add_field(name=text("oj.test_n_output",i+1), value=errors[i])
            await interaction.followup.send(embed=embed)

        async def on_error(self, interaction: discord.Interaction, error):
            print(error)  # prints error



    @app_commands.command(name="code", description=text("cmd.code.description"))
    @app_commands.describe(difficulty=text("cmd.code.difficulty"), id=text("cmd.code.id"))
    @app_commands.choices(
        difficulty = [
            Choice(name=text("oj.easy"), value=0),
            Choice(name=text("oj.normal"), value=1),
            Choice(name=text("oj.hard"), value=2)
        ]
    )
    async def code(self, interaction: discord.Interaction, difficulty: Choice[int], id: int):
        file_path = f"assets/code_test/{difficulty.value}/{id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                question = json.load(file)
            
            embed_main = discord.Embed(
                title=f"{question['name']}",
                description=f"{question['question']}\n\n  ",
                color=settings.Colors.oj
            )
            if "hint" in question:
                embed_main.add_field(name=text("cmd.code.hint"), value=question['hint'], inline=False)
            embed_main.add_field(name=text("cmd.code.input_format"), value=question['input_format'], inline=False)
            embed_main.add_field(name=text("cmd.code.output_format"), value=f"{question['output_format']}\n  ", inline=False)   
            embed_main.add_field(name=text("cmd.code.submit"), value=text("cmd.code.submit_description",self.diffToName(difficulty=difficulty.value),id))
            embed_main.set_footer(text=text("cmd.code.source",question['from']))
            if not os.path.exists(f"assets/code_test/{difficulty.value}/{id+1}.json"):
                embed_main.set_author(name=f"{self.diffToName(difficulty=difficulty.value)} #{id} {text('cmd.code.last')}")
            else:
                embed_main.set_author(name=f"{self.diffToName(difficulty=difficulty.value)} #{id}")

            embed_example = discord.Embed(
                title=text("cmd.code.example"),
                description="",
                color=settings.Colors.oj
            )
            examples = question["examples"]
            for i in range(len(examples)):
                embed_example.add_field(name=text("cmd.code.example_imput",i+1), value=examples[i]["input"], inline=False)
                embed_example.add_field(name=text("cmd.code.example_output",i+1), value=f"{examples[i]['output']}\n  ", inline=False)
                if "description" in examples[i]:
                    embed_example.add_field(name=text("cmd.code.example_des",i+1), value=examples[i]['description'], inline=False)

            await interaction.response.send_message(embeds=[embed_main, embed_example])
        else:
            await interaction.response.send_message(text("cmd.code.not_exist",self.diffToName(difficulty=difficulty.value),id), ephemeral=True)


    # --- Command: submit_code ---
    @app_commands.command(name="submit_code", description=text("cmd.code_submit.description"))
    @app_commands.describe(difficulty=text("cmd.code_submit.difficulty"), id=text("cmd.code_submit.id"), language=text("cmd.code_submit.lang"))
    @app_commands.choices(
        language=[
            Choice(name=text("cmd.code_submit.c_plus_plus"),value="cpp"),
            Choice(name=text("cmd.code_submit.c"),value="c")
        ],
        difficulty=[
            Choice(name=text("oj.easy"), value=0),
            Choice(name=text("oj.normal"), value=1),
            Choice(name=text("oj.hard"), value=2)
        ]
    )
    async def submit_code(self, interaction: discord.Interaction, difficulty: Choice[int], id: int, language: Choice[str]):
        if os.name == "nt":
            # only windows doesn't support bash commands
            await interaction.response.send_message(text("cmd.code_submit.winnt"))
            return
        file_path = f"assets/code_test/{difficulty.value}/{id}.json"
        if os.path.exists(file_path):
            global id_global, lang
            id_global = [difficulty.value, id]
            lang = language.value
            await interaction.response.send_modal(self.SubmitWindow())
        else:
            await interaction.response.send_message(text("cmd.code_submit.not_exist",self.diffToName(difficulty=difficulty.value),id), ephemeral=True)


async def setup(bot: commands.Bot):
    if os.name == "nt":
        # only windows doesn't support bash commands
        raise OSError(text("cmd.code_submit.winnt"))
    else:
        await bot.add_cog(OJ(bot))


