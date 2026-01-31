import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from aiohttp import web
import io
import json
import random
import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION (The Village Secrets) ---
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.environ.get("PORT", 8080)) # Render provides this automatically

# Channel IDs (Loaded from Environment Variables)
try:
    WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
    IMAGE_SOURCE_CHANNEL_ID = int(os.getenv("IMAGE_SOURCE_CHANNEL_ID"))
    CONFIG_CHANNEL_ID = int(os.getenv("CONFIG_CHANNEL_ID"))
except (TypeError, ValueError):
    print("❌ ERROR: One or more Channel IDs are missing from Environment Variables!")
    WELCOME_CHANNEL_ID = 0
    IMAGE_SOURCE_CHANNEL_ID = 0
    CONFIG_CHANNEL_ID = 0

# Admin IDs
ADMIN_IDS = [1410261255058493440]

# Image Settings
TEXT_CENTER_X = 1395
TEXT_CENTER_Y = 800
MAX_TEXT_WIDTH = 1052
FONT_PATH = "njnaruto.ttf"
DEFAULT_FONT_SIZE = 120

# Colors
COLOR_TOP = (0, 87, 183, 255)   # Naruto Blue
COLOR_BOTTOM = (255, 195, 0, 255) # Naruto Yellow

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class NarutoBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.bot_config = {"welcome_message": "Welcome {name} to the village! Enjoy your stay."}
        self.cached_image_urls = []

    async def setup_hook(self):
        # Start Web Server
        app = web.Application()
        app.router.add_get('/', self.handle_web_request)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        print(f"🌍 Web server started on port {PORT} - Ready for Cron Jobs!")

    async def handle_web_request(self, request):
        return web.Response(text="I'm awake! Dattebayo! 🍥", status=200)

bot = NarutoBot()

# --- MEMORY SYSTEM ---
async def save_config_to_discord():
    channel = bot.get_channel(CONFIG_CHANNEL_ID)
    if not channel: return
    json_data = json.dumps(bot.bot_config, indent=4)
    file_obj = io.BytesIO(json_data.encode("utf-8"))
    await channel.send(
        content=f"Create Date: {discord.utils.utcnow()}",
        file=discord.File(file_obj, filename="config.json")
    )

async def load_config_from_discord():
    channel = bot.get_channel(CONFIG_CHANNEL_ID)
    if not channel: return
    try:
        async for message in channel.history(limit=1):
            if message.attachments and message.attachments[0].filename.endswith(".json"):
                content = await message.attachments[0].read()
                bot.bot_config = json.loads(content)
                print("📜 Config scroll loaded!")
                return
    except Exception as e:
        print(f"Config load error: {e}")

async def refresh_image_cache():
    channel = bot.get_channel(IMAGE_SOURCE_CHANNEL_ID)
    if not channel: return
    new_cache = []
    async for message in channel.history(limit=50):
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                new_cache.append(attachment.url)
    bot.cached_image_urls = new_cache
    print(f"🖼️ Cached {len(bot.cached_image_urls)} background images.")

# --- IMAGE PROCESSING ---
def create_split_color_text(text, font):
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    height = bottom - top
    img_w, img_h = width + 20, height + 20

    mask = Image.new("L", (img_w, img_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.text((img_w/2, img_h/2), text, font=font, fill=255, anchor="mm")

    color_img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw_color = ImageDraw.Draw(color_img)
    draw_color.rectangle([(0, 0), (img_w, img_h / 2)], fill=COLOR_TOP)
    draw_color.rectangle([(0, img_h / 2), (img_w, img_h)], fill=COLOR_BOTTOM)

    final_text = Image.new("RGBA", (img_w, img_h), (0,0,0,0))
    final_text.paste(color_img, (0,0), mask=mask)
    return final_text

async def generate_welcome_card(user_name):
    if not bot.cached_image_urls: await refresh_image_cache()
    if not bot.cached_image_urls: return None

    bg_url = random.choice(bot.cached_image_urls)
    async with aiohttp.ClientSession() as session:
        async with session.get(bg_url) as resp:
            if resp.status != 200: return None
            data = await resp.read()

    bg_image = Image.open(io.BytesIO(data)).convert("RGBA")
    
    try:
        font_size = DEFAULT_FONT_SIZE
        font = ImageFont.truetype(FONT_PATH, font_size)
    except:
        font = ImageFont.load_default()

    text_width = font.getlength(user_name)
    while text_width > MAX_TEXT_WIDTH and font_size > 40:
        font_size -= 5
        font = ImageFont.truetype(FONT_PATH, font_size)
        text_width = font.getlength(user_name)

    text_image = create_split_color_text(user_name, font)
    
    w, h = text_image.size
    paste_x = int(TEXT_CENTER_X - (w / 2))
    paste_y = int(TEXT_CENTER_Y - (h / 2))

    bg_image.paste(text_image, (paste_x, paste_y), mask=text_image)
    
    output = io.BytesIO()
    bg_image.save(output, format="PNG")
    output.seek(0)
    return output

# --- SLASH COMMANDS (The New Jutsu) ---

@bot.tree.command(name="about", description="Shows info about this bot")
async def about(interaction: discord.Interaction):
    """Displays information about the bot using a slash command."""
    info_text = (
        "**Package Name:** Discord Welcome Bot\n"
        "**Package Version:** 1.0.1\n"
        "**Developed by:** PSBDx\n"
        "**License Type:** PSBDx Custom Open Source"
    )
    # Using interaction.response.send_message is required for slash commands
    await interaction.response.send_message(info_text)

# --- EVENTS & LEGACY COMMANDS ---

@bot.event
async def on_ready():
    print(f"🔥 Logged in as {bot.user}")
    await load_config_from_discord()
    await refresh_image_cache()
    
    # Sync Slash Commands to Discord
    # NOTE: This might take up to an hour to appear globally, but it's usually fast!
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"⚠️ Failed to sync commands: {e}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel: return
    
    msg_text = bot.bot_config["welcome_message"].format(
        name=member.mention, 
        user_name=member.name
    )
    img = await generate_welcome_card(member.name)
    if img:
        await channel.send(content=msg_text, file=discord.File(img, filename="welcome.png"))
    else:
        await channel.send(content=msg_text)

@bot.command()
async def set_welcome(ctx, *, message: str):
    if ctx.author.id not in ADMIN_IDS: return
    bot.bot_config["welcome_message"] = message
    await save_config_to_discord()
    await ctx.send("✅ Welcome message updated!")

@bot.command()
async def refresh_images(ctx):
    if ctx.author.id not in ADMIN_IDS: return
    await refresh_image_cache()
    await ctx.send(f"🔄 Refreshed {len(bot.cached_image_urls)} images.")

@bot.command()
async def test_welcome(ctx):
    if ctx.author.id not in ADMIN_IDS: return
    await ctx.send("⚡ Charging Chakra... (Generating Image)")
    img = await generate_welcome_card(ctx.author.name)
    if img:
        await ctx.send(content=bot.bot_config["welcome_message"].format(name=ctx.author.mention, user_name=ctx.author.name), file=discord.File(img, filename="test.png"))

bot.run(TOKEN)
