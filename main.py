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
    content = ctx.message.content
    user_id = content[3:].strip()

    if not user_id.isdigit():
        await ctx.send(f"❌ `{user_id}` không hợp lệ. Vui lòng nhập UID hợp lệ!")
        return

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

        embed = discord.Embed(
            title="📌 Kiểm tra trạng thái tài khoản",
            color=discord.Color.red() if is_banned else discord.Color.green()
        )
        embed.add_field(name="🆔 ID:", value=f"`{user_id}`", inline=False)

        embed.add_field(name="✅ Status", value="`success`", inline=True)
        embed.add_field(
            name="❗Thông báo",
            value="`Tài khoản đã bị BAN.`" if is_banned else "`The user is not banned.`",
            inline=True
        )

        if is_banned:
            status_text = f"🔴 **Tài khoản này đã bị khóa vĩnh viễn hoặc tạm thời!**\n📅 Thời gian ban: `{period}`"
            image_path = "assets/banned."
        else:
            status_text = "🟢 **Tài khoản của bạn hoàn toàn sạch và an toàn!**"
            image_path = "assets/notbanned.png"

        embed.add_field(name="📛 Trạng thái ACC", value=status_text, inline=False)
        embed.set_thumbnail(url="attachment://rank.png")  # Anh thay ảnh rank tương ứng
        embed.set_footer(
            text="📌 Dịch vụ kiểm tra tài khoản Free Fire • AURORAVN",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        embed.timestamp = ctx.message.created_at

        # Gửi file rank nếu có
        file = discord.File(image_path, filename="rank.png")
        await ctx.send(embed=embed, file=file)


bot.run(TOKEN)
