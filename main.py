import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN not set")

if not OWNER_ID:
    raise RuntimeError("❌ OWNER_ID not set")

OWNER_ID = int(OWNER_ID)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)  # ← เพิ่มตรงนี้!

# ========= PERMISSION =========
def is_owner(ctx):
    return ctx.author.id == OWNER_ID

def is_admin(ctx):
    return ctx.author.guild_permissions.administrator or is_owner(ctx)

# ========= EVENTS =========
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    owner = await bot.fetch_user(OWNER_ID)
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
