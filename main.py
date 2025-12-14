import os
import discord
from discord.ext import commands
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

# ========== โหลดจาก .env เท่านั้น ==========
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # ช่องฐานแม่ (ตัวเลข)

LINE_TOKEN = os.getenv("LINE_TOKEN")                  # Channel Access Token (long-lived)
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")             # Group ID ของ LINE

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")       # Group ID ของ Telegram (ติดลบ)

# เช็คค่าจำเป็น
if not DISCORD_TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN หาย! ใส่ใน .env ด้วย")
if not OWNER_ID:
    raise RuntimeError("❌ OWNER_ID หาย! ใส่ใน .env ด้วย")
if not DISCORD_CHANNEL_ID:
    print("⚠️ DISCORD_CHANNEL_ID หาย → Bridge Discord ไม่ทำงาน")
OWNER_ID = int(OWNER_ID)
DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID) if DISCORD_CHANNEL_ID else None

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.bans = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

# ========== Bridge Functions ==========
def send_to_line(text):
    if not LINE_TOKEN or not LINE_GROUP_ID:
        print("⚠️ LINE config หาย → ข้ามการส่ง")
        return
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"to": LINE_GROUP_ID, "messages": [{"type": "text", "text": text[:5000]}]}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"LINE error: {r.status_code} {r.text}")
    except Exception as e:
        print(f"ส่ง LINE ล้มเหลว: {e}")

def send_to_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram config หาย → ข้ามการส่ง")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text[:4096]}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print(f"Telegram error: {r.status_code} {r.text}")
    except Exception as e:
        print(f"ส่ง Telegram ล้มเหลว: {e}")

# ========== Events ==========
@bot.event
async def on_ready():
    print(f"✅ กองทัพตื่นแล้ว: {bot.user}")
    if DISCORD_CHANNEL_ID:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send("ฐานแม่ออนไลน์พร้อมรบ 24/7 💂‍♂️")

@bot.event
async def on_guild_join(guild):
    owner = await bot.fetch_user(OWNER_ID)
    await owner.send(f"⚠️ บอทถูกเพิ่มเข้าเซิร์ฟ: {guild.name}")

@bot.event
async def on_member_remove(member):
    if member == bot.user:
        owner = await bot.fetch_user(OWNER_ID)
        await owner.send(f"❌ บอทถูกเตะออกจากเซิร์ฟ: {member.guild.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Bridge: Discord ช่องฐานแม่ → LINE + Telegram
    if DISCORD_CHANNEL_ID and message.channel.id == DISCORD_CHANNEL_ID:
        text = f"[ฐานแม่ | {message.author.display_name}]: {message.content}"
        send_to_line(text)
        send_to_telegram(text)

    await bot.process_commands(message)

# ========== Commands ==========
@bot.command()
async def ping(ctx):
    await ctx.send(f"🟢 Online | Latency: {round(bot.latency*1000)}ms")

@bot.command()
async def menu(ctx):
    await ctx.send("🛒 รายการสินค้าประจำกองทัพ\n1️⃣ A\n2️⃣ B\n3️⃣ C")

@bot.command()
async def all(ctx):
    if ctx.author.id != OWNER_ID and not ctx.author.guild_permissions.administrator:
        return
    await ctx.message.delete()
    await ctx.send("@everyone มากองรวมพลด่วน!")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="ไม่ระบุ"):
    if ctx.author.id != OWNER_ID and not ctx.author.guild_permissions.administrator:
        return
    await member.kick(reason=reason)
    await ctx.send(f"👢 เตะ {member.mention} แล้ว")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="ไม่ระบุ"):
    if ctx.author.id != OWNER_ID and not ctx.author.guild_permissions.administrator:
        return
    await member.ban(reason=reason)
    await ctx.send(f"⛔ แบน {member.mention} แล้ว")

@bot.command(name="เย็ดแม่")
async def secret(ctx):
    await ctx.send("🤖 รับทราบคำสั่งระดับสูง")

# ========== RUN ==========
bot.run(DISCORD_TOKEN)async def on_ready():
    print(f"✅ กองทัพตื่นแล้ว: {bot.user} (ID: {bot.user.id})")
    print("พร้อมรบ 24/7 💂‍♂️")

@bot.event
async def on_guild_join(guild):
    owner = await bot.fetch_user(OWNER_ID)
    await owner.send(f"⚠️ บอทถูกเชิญเข้าเซิร์ฟใหม่: {guild.name} ({guild.member_count} คน)")

@bot.event
async def on_member_remove(member):
    if member == bot.user:
        owner = await bot.fetch_user(OWNER_ID)
        await owner.send(f"❌ บอทถูกเตะออกจากเซิร์ฟ: {member.guild.name}")

# ========== COMMANDS ==========
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📌 คำสั่งกองทัพ", color=0xFF0000)
    embed.add_field(name="พื้นฐาน", value="/help\n/menu\n/ping", inline=False)
    embed.add_field(name="แอดมินเท่านั้น", value="/all\n/kick @user\n/ban @user\n/unban user_id", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def menu(ctx):
    await ctx.send("🛒 **รายการสินค้าประจำกองทัพ**\n1️⃣ สินค้า A - ราคา X\n2️⃣ สินค้า B - ราคา Y\n3️⃣ สินค้า C - ราคา Z\nสนใจทักแอดมิน!")

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🟢 ฐานแม่ออนไลน์ | Latency: {latency}ms")

@bot.command()
async def all(ctx):
    if not is_admin(ctx):
        await ctx.send("❌ สิทธิ์ไม่พอ!")
        return
    await ctx.message.delete()  # ลบคำสั่งเพื่อความเรียบร้อย
    await ctx.send("@everyone มากองรวมพลด่วน! 💂‍♂️")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="ไม่ระบุเหตุผล"):
    if not is_admin(ctx):
        await ctx.send("❌ สิทธิ์ไม่พอ!")
        return
    await member.kick(reason=reason)
    await ctx.send(f"👢 เตะ {member.mention} ออกจากกองทัพแล้ว\nเหตุผล: {reason}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="ไม่ระบุเหตุผล"):
    if not is_admin(ctx):
        await ctx.send("❌ สิทธิ์ไม่พอ!")
        return
    await member.ban(reason=reason)
    await ctx.send(f"⛔ แบน {member.mention} ถาวร\nเหตุผล: {reason}")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_admin(ctx):
        await ctx.send("❌ สิทธิ์ไม่พอ!")
        return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ ปลดแบน {user.name} กลับสู่กองทัพ")
    except discord.NotFound:
        await ctx.send("❌ ไม่พบผู้ใช้หรือยังไม่ได้แบน")

@bot.command(name="เย็ดแม่")
async def secret_cmd(ctx):
    if not is_owner(ctx):
        await ctx.send("🤨 มึงคิดว่ามึงเป็นใคร?")
        return
    await ctx.send("🤖 รับทราบคำสั่งระดับสูงสุดจากท่านผู้บัญชาการ!")

# ========== สำหรับ Bridge ในอนาคต (ไม่ลืม override on_message) ==========
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # ที่นี่จะใส่ bridge logic ในภายหลัง เช่น ถ้าส่งในช่องฐานแม่ → forward ไป LINE/Tele
    await bot.process_commands(message)

# ========== RUN ==========
bot.run(TOKEN)    owner = await bot.fetch_user(OWNER_ID)
    await owner.send(f"⚠️ บอทถูกเพิ่มเข้า: {guild.name}")

@bot.event
async def on_member_remove(member):
    if member == bot.user:
        owner = await bot.fetch_user(OWNER_ID)
        await owner.send("❌ บอทถูกเตะออกจากกลุ่ม!")

# ========= BASIC =========
@bot.command()
async def help(ctx):
    await ctx.send("""
📌 คำสั่งบอท
/kick @user
/ban @user
/unban user_id
/all
/menu
/help
""")

@bot.command()
async def menu(ctx):
    await ctx.send("🛒 รายการสินค้า\n1️⃣ A\n2️⃣ B\n3️⃣ C")

@bot.command()
async def all(ctx):
    if not is_admin(ctx):
        return
    mentions = " ".join(m.mention for m in ctx.guild.members if not m.bot)
    await ctx.send(mentions)

# ========= ADMIN =========
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=""):
    if not is_admin(ctx):
        return
    await member.kick(reason=reason)
    await ctx.send(f"👢 เตะ {member.mention}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=""):
    if not is_admin(ctx):
        return
    await member.ban(reason=reason)
    await ctx.send(f"⛔ แบน {member.mention}")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_admin(ctx):
        return
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ ปลดแบน {user.name}")

# ========= CUSTOM TEXT =========
@bot.command()
async def เย็ดแม่(ctx):
    await ctx.send("🤖 รับทราบคำสั่งระดับสูง")

bot.run(TOKEN)

from dotenv import load_dotenv
load_dotenv(override=True)
