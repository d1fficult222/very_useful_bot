import discord
from discord import File
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import random, io, json, datetime, uuid
import settings
from lang import *



ANS_LIST_PATHS = {"5": "assets/wordle/answers.txt"}
ALLOWED_LIST_PATHS = {"5": "assets/wordle/allowed_guesses.txt"}

ans_list = {}
allowed_list = {}
for key, value in ANS_LIST_PATHS.items():
    with open(value, "r") as f:
        ans_list[key] = [i.strip().upper() for i in f.readlines()]
for key, value in ALLOWED_LIST_PATHS.items():
    with open(value, "r") as f:
        allowed_list[key] = [i.strip().upper() for i in f.readlines()]

STATS_PATH = "assets/stats.json"
FONTS_PATH = [r"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arial.ttf"]



class WordleGame:
    def __init__(self, player, answer, word_length, attempts):
        self.player: discord.User | discord.Member = player
        self.ANSWER: str = answer
        self.WORD_LENGTH: int = word_length
        self.ATTEMPTS: int = attempts
        self.GAME_ID: str = str(uuid.uuid4())[:8].upper()
        self.last_played: datetime = datetime.datetime.now()
        self.last_message = None
        self.guesses: list = []
        self.results: list = []
        self.green_letter: list = []
        self.yellow_letter: list = []
        self.black_letter: list = []
        self.other_letter: list = [chr(i) for i in range(ord('A'), ord('Z')+1)]  # A to Z
        self.ended: bool = False

    def submit_guess(self, guess: str) -> str:
        """
        處理 guess，並將結果更新到 self.guesses, self.result 等  
        回傳: 'win' 代表贏，'lose' 代表輸，'continue' 代表遊戲繼續
        """

        if self.ended:
            raise RuntimeError(text("遊戲已結束"))

        # 將 guess 去除空白並大寫
        guess = str(guess).strip()
        try:
            guess = guess.upper()
        except Exception:
            raise ValueError(text("wordle.error.upper", guess))

        # 檢查單字長度
        length = len(guess)
        if length != self.WORD_LENGTH:
            raise ValueError(text("wordle.error.length", guess, length, self.WORD_LENGTH))
        
        # 判斷單字是否在清單中
        answers = ans_list.get(str(self.WORD_LENGTH), None)
        allowed = ans_list.get(str(self.WORD_LENGTH), None)
        if not answers or not allowed:
            raise FileNotFoundError(text("wordle.error.fnf", self.WORD_LENGTH))
        if not(guess in answers or guess in allowed):
            raise ValueError(text("wordle.error.not_in", guess))
        
        # 處理猜測
        result = ['B'] * length
        # 統計答案字母，例如 "SPEED" -> {'S': 1, 'P': 1, 'E': 2, 'D': 1}
        ans_letter_count = {}
        for i in self.ANSWER:
            ans_letter_count[i] = ans_letter_count.get(i, 0) + 1
        # 標記綠色
        for i in range(length):
            if guess[i] == self.ANSWER[i]:
                result[i] = 'G'
                ans_letter_count[guess[i]] -= 1
                # 更新 self.green_letter, self.yellow_letter, self.black_letter, self.other_letter
                if guess[i] not in self.green_letter:
                    self.green_letter.append(guess[i])
                if guess[i] in self.yellow_letter:
                    self.yellow_letter.remove(guess[i])
                if guess[i] in self.black_letter:
                    self.black_letter.remove(guess[i])
                if guess[i] in self.other_letter:
                    self.other_letter.remove(guess[i])
        # 標記黃色與黑色
        for i in range(length):
            if result[i] != 'G' and ans_letter_count.get(guess[i], 0) > 0:
                result[i] = 'Y'
                ans_letter_count[guess[i]] -= 1
                # 更新 self.yellow_letter, self.black_letter, self.other_letter
                if guess[i] not in self.yellow_letter:
                    self.yellow_letter.append(guess[i])
                if guess[i] in self.black_letter:
                    self.black_letter.remove(guess[i])
                if guess[i] in self.other_letter:
                    self.other_letter.remove(guess[i])
            if result[i] == 'B':
                letter = guess[i]
                if letter not in self.green_letter and letter not in self.yellow_letter:
                    if letter not in self.black_letter:
                        self.black_letter.append(letter)
                if letter in self.other_letter:
                    self.other_letter.remove(letter)
        self.green_letter = sorted(self.green_letter)
        self.yellow_letter = sorted(self.yellow_letter)
        self.black_letter = sorted(self.black_letter)

        # 更新 self.results, self.guesses, 統計資料與判斷輸贏
        self.results.append(result)
        self.guesses.append([i for i in guess])
        self.last_played = datetime.datetime.now()
        
        status = "continue"
        if guess == self.ANSWER:
            status = "win"
            self.ended = True
        elif len(self.guesses) >= self.ATTEMPTS:
            status = "lose"
            self.ended = True
        
        if status != "continue":
            try:
                with open(STATS_PATH, 'r') as f:
                    stats: dict = json.load(f)
            except json.JSONDecodeError:
                stats = {}
            if not stats:
                stats = {}
            stats.setdefault("wordle", {"times_played": 0, "players": {}})
            stats["wordle"]["times_played"] += 1
            stats["wordle"]["players"].setdefault(f"{self.player.id}", {
                    "played": 0,
                    "win": 0,
                    "lose": 0,
                    "streak": 0
                })
            player = stats["wordle"]["players"][f"{self.player.id}"]
            player["played"] += 1
            if status == "win":
                player["win"] += 1
                player["streak"] += 1
            else:
                player["lose"] += 1
                player["streak"] = 0
            with open(STATS_PATH, "w") as f:
                json.dump(stats, f, indent=4)
        
        return status

    def draw_image(self) -> io.BytesIO:
        """
        繪製結果圖片，儲存在 buffer
        """
        # 參數
        BLOCK_SIZE = 45
        MARGIN = 5
        BACKGROUND = text("wordle.color.background")
        WHITE = text("wordle.color.white")
        GREEN = text("wordle.color.green")
        YELLOW = text("wordle.color.yellow")
        BLACK = text("wordle.color.black")
        FONT = None
        for i in FONTS_PATH:
            try:
                FONT = ImageFont.truetype(i, round(BLOCK_SIZE * 3 / 5))
                break
            except:
                continue
        if not FONT:
            FONT = ImageFont.load_default()
        # 繪製
        image_width = (BLOCK_SIZE + MARGIN) * self.WORD_LENGTH - MARGIN
        image_height = (BLOCK_SIZE + MARGIN) * self.ATTEMPTS - MARGIN
        image = Image.new("RGB", (image_width, image_height), color=BACKGROUND)
        draw = ImageDraw.Draw(image)
        for i in range(self.ATTEMPTS):
            for j in range(self.WORD_LENGTH):
                x1 = j * (BLOCK_SIZE + MARGIN)
                y1 = i * (BLOCK_SIZE + MARGIN)
                x2 = x1 + BLOCK_SIZE
                y2 = y1 + BLOCK_SIZE
                try:
                    match self.results[i][j]:
                        case 'G': color = GREEN
                        case 'Y': color = YELLOW
                        case 'B': color = BLACK
                    block_text = self.guesses[i][j]
                    draw.rectangle([x1, y1, x2, y2], fill=color)
                    bbox = FONT.getbbox(block_text)
                    txt_width = bbox[2] - bbox[0]
                    txt_height = bbox[3] - bbox[1]
                    txt_x = x1 + (BLOCK_SIZE - txt_width) // 2
                    txt_y = y1 + (BLOCK_SIZE - txt_height) // 2
                    draw.text((txt_x, txt_y), block_text, fill=WHITE, font=FONT)
                except:
                    draw.rectangle([x1, y1, x2, y2], fill=BLACK)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')    
        buffer.seek(0)
        return buffer

    def generate_embed(self, player_data: dict) -> dict:
            """
            回傳一個 dictionary，包含遊戲結果的 Embed 與 View
            """
            return_dict = {}
            if self.ended:
                view = discord.ui.View()
                last_guess = ''.join(self.guesses[-1])
                embed = discord.Embed(
                    title=text("wordle.you_win", last_guess) if last_guess == self.ANSWER else text("wordle.you_lose", last_guess),
                    description="" if last_guess == self.ANSWER else text("wordle.ans_was", self.ANSWER),
                    color=settings.Colors.wordle
                )
                try:
                    with open(STATS_PATH, 'r') as f:
                        stats: dict = json.load(f)
                    player = stats["wordle"]["players"][f"{self.player.id}"]
                    embed.add_field(name=text("wordle.games_played"), value=player.get("played", 1))
                    embed.add_field(name=text("wordle.games_won"), value=player.get("win", 0))
                    embed.add_field(name=text("wordle.win_rate"), value=player.get("win", 0)/player.get("played", 1))
                    embed.add_field(name=text("wordle.streak"), value=player.get("streak", 0))
                except:
                    pass
                translate_button = discord.ui.Button(label=text("wordle.translate"), emoji=text("wordle.translate.emoji"), disabled=True)
                share_button = discord.ui.Button(label=text("wordle.share"), emoji=text("wordle.share.emoji"))
                async def share_button_callback(interaction: discord.Interaction):
                    await interaction.response.send_message(text("wordle.share.message", interaction.user.mention))
                share_button.callback = share_button_callback
                view.add_item(translate_button)
                view.add_item(share_button)
            else:
                embed = discord.Embed(
                    title=f"{len(self.guesses)}/{self.ATTEMPTS}: {''.join(self.guesses[-1])}",
                    description="",
                    color=settings.Colors.wordle,
                    timestamp=datetime.datetime.now()
                )
                if len([i for i in self.green_letter]) != 0:
                    embed.add_field(name=text("wordle.correct"), value=" ".join(i for i in self.green_letter))
                if len([i for i in self.yellow_letter]) != 0:
                    embed.add_field(name=text("wordle.wrong_pos"), value=" ".join(i for i in self.yellow_letter))
                if len([i for i in self.black_letter]) != 0:
                    embed.add_field(name=text("wordle.incorrect"), value=" ".join(i for i in self.black_letter))
                embed.add_field(name=text("wordle.havent_tried"), value=" ".join(i for i in self.other_letter))
                view = discord.ui.View()
                hint_button = discord.ui.Button(label=text("wordle.hint"), emoji=text("wordle.hint.emoji"), disabled=True)
                ask_ai_button = discord.ui.Button(label=text("wordle.askai"), emoji=text("wordle.askai.emoji"), disabled=True)
                end_button = discord.ui.Button(label=text("wordle.end"), emoji=text("wordle.end.emoji"), style=discord.ButtonStyle.red)
                async def end_button_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    embed = discord.Embed(
                        title=text("wordle.ended.title"),
                        description=text("wordle.ended.description", self.ANSWER),
                        color=settings.Colors.wordle,
                        timestamp=datetime.datetime.now()
                    )
                    player_data.pop(self.player.id, None)
                    await interaction.message.edit(embed=embed, view=None)
                end_button.callback = end_button_callback
                view.add_item(hint_button)
                view.add_item(ask_ai_button)
                view.add_item(end_button)

            try:
                with open(STATS_PATH, 'r') as f:
                    stats: dict = json.load(f)
                embed.set_author(name=f"[{self.player.display_name}] Wordle #{stats['wordle']['players'][str(self.player.id)]['played']}", icon_url=self.player.display_avatar.url)
            except:
                embed.set_author(name=f"{self.player.display_name}", icon_url=self.player.display_avatar.url)
            embed.set_footer(text=f"#{self.GAME_ID}")
            return_dict["embed"] = embed
            return_dict["view"] = view
            return return_dict            
            


class Wordle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player_data: dict = {}
    
    def cog_unload(self):
        self.bot.remove_command("wordle")
    
    @commands.hybrid_command(name="wordle", description=text("wordle.cmd.description"))
    async def wordle(self, ctx: commands.Context, guess: str):
        
        def start_new_game() -> WordleGame:
            """
            建立新遊戲 (length 5)
            """
            answers = ans_list.get("5", None)
            if not answers:
                raise FileNotFoundError(text("wordle.error.fnf", 5))
            
            game = WordleGame(
                player=ctx.author,
                answer=random.choice(answers),
                word_length=5,
                attempts=6
            )
            self.player_data[ctx.author.id] = game
            return game
        
        async def process_guess(game: WordleGame) -> None:
            """
            Submit the guess, draw image, and send results
            """
            try:
                game.submit_guess(guess)
            except ValueError as e:
                await ctx.send(e, delete_after=3)
                return
            except FileNotFoundError as e:
                await ctx.send(text("wordle.error", e))
                return
            
            # 刪除上一則訊息
            if game.last_message:
                try:
                    await game.last_message.delete()
                except discord.NotFound:
                    pass
                except discord.HTTPException:
                    pass

            # 發送訊息，並記錄這則訊息供下次刪除
            image_buffer = game.draw_image()
            attatchments = game.generate_embed(self.player_data)
            game.last_message = await ctx.send(
                file=File(image_buffer, text("wordle.image.filename", game.GAME_ID, len(game.guesses), game.ATTEMPTS).removesuffix(".png") + ".png"),
                embed=attatchments.get("embed", None),
                view=attatchments.get("view", None)
            )

            # 結束就從 player_data 中移除
            if game.ended:
                self.player_data.pop(ctx.author.id, None)


        game: WordleGame = self.player_data.get(ctx.author.id, None)
        if not game:
            # 使用者不在 playerdata 內，建立新遊戲
            game = start_new_game()
            await process_guess(game)
        else:
            # 判斷與上一場遊戲間隔是否超過一天
            if abs(datetime.datetime.now() - game.last_played).total_seconds() > 86400:
                embed = discord.Embed(
                    title=text("wordle.continue.title"),
                    description=text("wordle.continue.description")
                )
                embed.add_field(
                    name=text("wordle.continue.time"),
                    value=game.last_played.strftime("%Y-%m-%d, %H:%M:%S")
                )
                embed.add_field(
                    name=text("wordle.continue.gameid"),
                    value=game.GAME_ID
                )
                view = discord.ui.View()
                continue_button = discord.ui.Button(label=text("wordle.continue.continue"), emoji=text("wordle.continue.continue.emoji"))     # 保留並繼續遊戲
                restart_button = discord.ui.Button(label=text("wordle.continue.restart"), emoji=text("wordle.continue.restart.emoji"))        # 刪除並重新開始
                keep_exit_button = discord.ui.Button(label=text("wordle.continue.keep_exit"), emoji=text("wordle.continue.keep_exit.emoji"))  # 保留並離開
                del_exit_button = discord.ui.Button(label=text("wordle.continue.del_exit"), emoji=text("wordle.continue.del_exit.emoji"))     # 刪除並離開

                async def continue_button_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    await interaction.message.delete()
                    await process_guess(game)

                async def restart_button_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    await interaction.message.delete()
                    nonlocal game
                    game = start_new_game()
                    await process_guess(game)

                async def keep_exit_button_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    await interaction.message.delete()

                async def del_exit_button_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    await interaction.message.delete()
                    self.player_data.pop(ctx.author.id, None)

                continue_button.callback = continue_button_callback
                restart_button.callback = restart_button_callback
                keep_exit_button.callback = keep_exit_button_callback
                del_exit_button.callback = del_exit_button_callback
                view.add_item(continue_button)
                view.add_item(restart_button)
                view.add_item(keep_exit_button)
                view.add_item(del_exit_button)
                await ctx.send(embed=embed, view=view)
            else:
                await process_guess(game)
                if ctx.message:
                    try:
                        await ctx.message.delete()
                    except (discord.errors.Forbidden, discord.NotFound, discord.HTTPException):
                        pass
            


async def setup(bot: commands.Bot):
    await bot.add_cog(Wordle(bot))