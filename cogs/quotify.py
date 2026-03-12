import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp, io, re
from lang import *


class Quotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.bot.remove_command("quotify")


@app_commands.context_menu(name=text("menu.quotify"))
async def quotify(interaction: discord.Interaction, message: discord.Message):
    user = message.author
    url = user.display_avatar.replace(size=256).url

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                await interaction.response.send_message(text("menu.quotify.fail"))
            data = await r.read()

    avatar = Image.open(io.BytesIO(data)).convert("RGBA")
    
    # Settings
    WIDTH = 960
    HEIGHT = 540
    AVATAR_SIZE = 400
    FONT_SIZE = 50
    PADDING = 30
    BACKGROUND = "#212121"

    # Background
    background = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    
    # Avatar
    avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE))
    background.paste(avatar, (PADDING, (HEIGHT-AVATAR_SIZE)//2), avatar)
    
    # Font
    try:
        font1 = ImageFont.truetype(r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", FONT_SIZE)
        font2 = ImageFont.truetype(r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", FONT_SIZE//2)
    except:
        try:
            font1 = ImageFont.truetype("arial.ttf", FONT_SIZE)
            font2 = ImageFont.truetype("arial.ttf", FONT_SIZE//2)
        except:
            font1 = ImageFont.load_default()
            font2 = ImageFont.load_default()
    
    # Word wrap
    def wrap(text, font, max_width):
        lines = []
        current_line = ""
        # Match: single CJK characters, English words, or punctuation/symbols
        tokens = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]+|[^\s\w]', text)
        for i in tokens:
            if re.match(r'[a-zA-Z0-9]', i) and current_line and not current_line.endswith(' '):
                # Chinese: add space between characters
                test_line = current_line + ' ' + i
            else:
                # English: space is already there
                test_line = current_line + i
            if font.getlength(test_line.strip()) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = i
        if current_line:
            lines.append(current_line.strip())
        return lines

    # Content
    quote_text = message.content
    if not quote_text and message.embeds:
        embed = message.embeds[0]
        quote_text = embed.description or embed.title or ""
    if not quote_text:
        await interaction.response.send_message(text("menu.quotify.no_content"))
        return

    text1_max_w = WIDTH - AVATAR_SIZE - PADDING * 3
    wrapped = wrap(f'"{quote_text}"', font1, text1_max_w)
    text_content = "\n".join(wrapped)
    draw1 = ImageDraw.Draw(background)
    text1_w, text1_h = draw1.textsize(text_content, font=font1)
    draw1.multiline_text((AVATAR_SIZE+PADDING*2, (HEIGHT-text1_h)//2), text_content, font=font1, fill="white", spacing=4)

    # Author
    text_author = f"-- {user.display_name}"
    draw2 = ImageDraw.Draw(background)
    text2_w, text2_h = draw2.textsize(text_author, font=font2)
    draw2.text((WIDTH-text2_w-PADDING, HEIGHT-text2_h-PADDING), text_author, font=font2, fill="white")

    # Save
    output = io.BytesIO()
    background.save(output, format="PNG")
    output.seek(0)

    # Send
    file = discord.File(output, filename="quotify.png")
    await interaction.response.send_message(file=file)
    
async def setup(bot: commands.Bot):
    bot.tree.add_command(quotify)