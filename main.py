import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
from utils import check_ban

app = Flask(__name__)

load_dotenv()
APPLICATION_ID = os.getenv("APPLICATION_ID")
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DEFAULT_LANG = "en"
user_languages = {}

nomBot = "None"

@app.route('/')
def home():
    global nomBot
    return f"Bot {nomBot} is working"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask).start()

@bot.event
async def on_ready():
    global nomBot
    nomBot = f"{bot.user}"
    print(f"Le bot est connecté en tant que {bot.user}")

@bot.command(name="guilds")
async def show_guilds(ctx):
    guild_names = [f"{i+1}. {guild.name}" for i, guild in enumerate(bot.guilds)]
    guild_list = "\n".join(guild_names)
    await ctx.send(f"Le bot est dans les guilds suivantes :\n{guild_list}")

@bot.command(name="lang")
async def change_language(ctx, lang_code: str):
    lang_code = lang_code.lower()
    if lang_code not in ["en", "fr"]:
        await ctx.send("❌ Invalid language. Available: `en`, `fr`")
        return

    user_languages[ctx.author.id] = lang_code
    message = "✅ Language set to English." if lang_code == 'en' else "✅ Langue définie sur le français."
    await ctx.send(f"{ctx.author.mention} {message}")

@bot.command(name="ID")
async def check_ban_command(ctx):
    import re, time

    content = ctx.message.content
    match = re.search(r'\b\d{5,20}\b', content)
    user_id = match.group(0) if match else None

    if not user_id:
        await ctx.send("❌ Không tìm thấy UID hợp lệ. Nhập đúng dạng: `@ID 123456789`")
        return

    start = time.perf_counter()
    async with ctx.typing():
        try:
            ban_status = await check_ban(user_id)
        except Exception as e:
            await ctx.send(f"⚠️ Lỗi khi kiểm tra UID:\n```{str(e)}```")
            return

    if ban_status is None:
        await ctx.send("❌ Không lấy được thông tin. Vui lòng thử lại sau.")
        return

    is_banned = int(ban_status.get("is_banned", 0))
    nickname = ban_status.get("nickname", "N/A")
    region = ban_status.get("region", "N/A")
    period = ban_status.get("period", "N/A")

    if is_banned:
        status_text = f"🔴 **Tài khoản này đã bị khóa!**\n📅 Thời gian ban: `{period}`"
        image_path = "assets/banned."
        thong_bao = "🔒 Banned"
    else:
        status_text = "🟢 **Tài khoản hoàn toàn sạch và an toàn!**"
        image_path = "assets/notbanned.png"
        thong_bao = "🔓 Not banned"

    embed = discord.Embed(
        title="📌 Kiểm tra trạng thái tài khoản",
        color=discord.Color.from_rgb(157, 78, 221),  # Màu tím viền trái
        description=f"🆔 **ID:** `{user_id}`"
    )

    # Hàng 1
    embed.add_field(name="📋 Status", value="✅ success", inline=True)
    embed.add_field(name="⚠️ Thông báo", value=thong_bao, inline=True)

    # Hàng 2
    embed.add_field(name="👤 Nickname", value=f"`{nickname}`", inline=True)
    embed.add_field(name="🌍 Region", value=f"`{region}`", inline=True)

    # Hàng 3
    embed.add_field(name="📛 Trạng thái ACC", value=status_text, inline=False)

    # Ảnh
    embed.set_thumbnail(url="attachment://rank.gif")

    end = time.perf_counter()
    embed.set_footer(
        text=f"📌 Dịch vụ kiểm tra tài khoản Free Fire • AURORAVN • {ctx.message.created_at.strftime('%H:%M %d/%m/%y')} • Xử lý {end - start:.2f}s",
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )

    file = discord.File(image_path, filename="rank.gif")
    await ctx.send(embed=embed, file=file)


bot.run(TOKEN)
