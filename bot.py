import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
import random
from datetime import timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Database for levels & top member
conn = sqlite3.connect('server_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS levels (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1)''')
c.execute('''CREATE TABLE IF NOT EXISTS current_top (user_id INTEGER)''')
conn.commit()

# Level brackets (customize thresholds as needed)
LEVEL_ROLES = {
    1: "Rookie",
    10: "Drill Soldier",
    50: "OTF Warrior",
    100: "Slime Killer",
    500: "X Legacy",
    2000: "Gang King",
    10000: "Ultimate Drill King"
}

BLOCKED_KEYWORDS = ["lil tim", "quando", "chief keef"]

async def get_user_level(user_id):
    c.execute("SELECT xp, level FROM levels WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        return 0, 1
    return row[0], row[1]

async def add_xp(user_id, amount=25):
    xp, level = await get_user_level(user_id)
    new_xp = xp + amount
    new_level = int((new_xp ** 0.5) / 5) + 1  # Formula allows 64,000+ levels easily
    c.execute("INSERT OR REPLACE INTO levels (user_id, xp, level) VALUES (?, ?, ?)", (user_id, new_xp, new_level))
    conn.commit()
    return new_level > level, new_level  # leveled_up, current_level

async def update_top_drill(guild):
    c.execute("SELECT user_id, level FROM levels ORDER BY level DESC LIMIT 1")
    top = c.fetchone()
    if not top:
        return
    top_role = discord.utils.get(guild.roles, name="🏆 Top Drill Member")
    if not top_role:
        return
    for member in guild.members:
        if top_role in member.roles:
            await member.remove_roles(top_role)
    top_member = guild.get_member(top[0])
    if top_member:
        await top_member.add_roles(top_role)

# ====================== SERVER SETUP COMMAND ======================
@bot.command(name="LLKV")
@commands.has_permissions(administrator=True)
async def llkv(ctx):
    guild = ctx.guild
    await ctx.send("🔥 **LLKV SERVER SETUP STARTING** 🔥\nThis will take ~30 seconds...")

    # 1. Create Roles
    role_names = {
        "👑 Owner": discord.Color.gold(),
        "🏆 Top Drill Member": discord.Color.red(),
        "🛠️ Moderator": discord.Color.blue(),
        "💬 Member": discord.Color.light_gray(),
        "🩸 OBlock": discord.Color(0x8B0000),
        "🔥 OTF": discord.Color(0xFF4500),
        "🐍 Slime": discord.Color(0x00FF00),
        "⚡ X Gang": discord.Color(0x00BFFF),
        "🎁 Giveaway Manager": discord.Color.purple()
    }
    created_roles = {}
    for name, color in role_names.items():
        role = discord.utils.get(guild.roles, name=name)
        if not role:
            role = await guild.create_role(name=name, color=color, hoist=True)
        created_roles[name] = role

    # Give Owner role to server owner + the admin who ran command
    await guild.owner.add_roles(created_roles["👑 Owner"])
    await ctx.author.add_roles(created_roles["👑 Owner"])

    # 2. Create Categories & Channels + Permissions
    categories = {
        "👑 𝕶𝖎𝖓𝖌 𝖁𝖔𝖓 𝕺𝕭𝖑𝖔𝖈𝖐": ["von-chat", "von-music", "oblock-pics", "von-vc"],
        "🔥 𝕷𝖎𝖑 𝕯𝖚𝖗𝖐 𝕺𝕿𝕱": ["durk-chat", "durk-music", "otf-drip", "durk-vc"],
        "🐍 𝖄𝕹𝖂 𝕸𝖊𝖑𝖑𝖞 𝕾𝖑𝖎𝖒𝖊": ["melly-chat", "melly-music", "ynw-pics", "melly-vc"],
        "⚡ 𝕏 𝕷𝖊𝖌𝖆𝖈𝖞": ["x-chat", "x-music", "x-quotes", "x-vc"],
        "🩸 𝕷𝖎𝖑 𝕵𝖊𝖋𝖋 𝕲𝖆𝖓𝖌": ["jeff-chat", "jeff-music", "jeff-pics", "jeff-vc"],
        "🌍 𝕲𝖊𝖓𝖊𝖗𝖆𝖑": ["general-chat", "music-share", "pics", "general-vc", "welcome"],
        "🔒 𝕻𝖗𝖎𝖛𝖆𝖙𝖊 𝕾𝖙𝖆𝖋𝖋": ["mod-chat", "owner-chat", "oblock-chat", "staff-logs"],
        "🎉 GIVEAWAYS & SPECIAL": ["giveaway-announcements", "giveaway-role", "Cali-Streets", "Deadly-Von-Gang", "Partnerships", "Apply-for-Roles"]
    }

    for cat_name, channels in categories.items():
        category = await guild.create_category(cat_name)
        for ch_name in channels:
            if "vc" in ch_name.lower():
                await guild.create_voice_channel(ch_name, category=category)
            else:
                await guild.create_text_channel(ch_name, category=category)
            await asyncio.sleep(0.5)  # Rate limit safety

    # 3. Set Permissions (staff channels locked)
    everyone = guild.default_role
    mod_role = created_roles["🛠️ Moderator"]
    owner_role = created_roles["👑 Owner"]
    giveaway_role = created_roles["🎁 Giveaway Manager"]

    # Example: mod-chat only mods+
    mod_chat = discord.utils.get(guild.channels, name="mod-chat")
    if mod_chat:
        await mod_chat.set_permissions(everyone, read_messages=False)
        await mod_chat.set_permissions(mod_role, read_messages=True, send_messages=True)
        await mod_chat.set_permissions(owner_role, read_messages=True, send_messages=True)

    # owner-chat & oblock-chat only Owner
    for name in ["owner-chat", "oblock-chat"]:
        ch = discord.utils.get(guild.channels, name=name)
        if ch:
            await ch.set_permissions(everyone, read_messages=False)
            await ch.set_permissions(owner_role, read_messages=True, send_messages=True)

    # giveaway-announcements only Giveaway Manager + mods
    ga = discord.utils.get(guild.channels, name="giveaway-announcements")
    if ga:
        await ga.set_permissions(everyone, read_messages=True, send_messages=False)
        await ga.set_permissions(giveaway_role, send_messages=True)

    await ctx.send("✅ **FULL SERVER SETUP COMPLETE!** All categories, channels, roles, and permissions are done.")

# ====================== EVENTS ======================
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    await bot.tree.sync()

@bot.event
async def on_member_join(member):
    # Welcome
    welcome_channel = discord.utils.get(member.guild.channels, name="welcome")
    if welcome_channel:
        await welcome_channel.send(f"Welcome to the Drill Server 🔥 {member.mention}\nChat, level up, and become the Top Drill Member.")

    # Username block
    if any(kw in member.display_name.lower() for kw in BLOCKED_KEYWORDS):
        await member.timeout(timedelta(days=7), reason="Blocked name")
        try:
            await member.send("Your username contains a blocked term. Timed out for 7 days.")
        except:
            pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Block messages
    if any(kw in message.content.lower() for kw in BLOCKED_KEYWORDS):
        await message.delete()
        await message.author.timeout(timedelta(days=7), reason="Blocked term")
        return

    # Level system
    leveled_up, new_level = await add_xp(message.author.id)
    if leveled_up:
        # Assign level role
        for threshold, role_name in sorted(LEVEL_ROLES.items(), reverse=True):
            if new_level >= threshold:
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role:
                    await message.author.add_roles(role)
                break
        await update_top_drill(message.guild)
        await message.channel.send(f"🎉 {message.author.mention} leveled up to **{new_level}**!")

    await bot.process_commands(message)

# ====================== SLASH COMMANDS (Admin only) ======================
@bot.tree.command(name="setup")
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("Use `!LLKV` for full setup!")

@bot.tree.command(name="addlevel")
@app_commands.default_permissions(administrator=True)
async def addlevel(interaction: discord.Interaction, user: discord.Member, xp: int):
    await add_xp(user.id, xp)
    await update_top_drill(interaction.guild)
    await interaction.response.send_message(f"Added {xp} XP to {user.mention}")

@bot.tree.command(name="top")
@app_commands.default_permissions(administrator=True)
async def top(interaction: discord.Interaction):
    c.execute("SELECT user_id, level FROM levels ORDER BY level DESC LIMIT 5")
    tops = c.fetchall()
    msg = "**Top Drill Members:**\n"
    for i, (uid, lvl) in enumerate(tops, 1):
        member = interaction.guild.get_member(uid)
        msg += f"{i}. {member.mention if member else 'Unknown'} — Level {lvl}\n"
    await interaction.response.send_message(msg)

@bot.tree.command(name="resetserver")
@app_commands.default_permissions(administrator=True)
async def resetserver(interaction: discord.Interaction):
    await interaction.response.send_message("⚠️ This would delete everything. Not implemented for safety. Use !LLKV on a fresh server instead.")

# ====================== GIVEAWAY SYSTEM ======================
class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = []

    @discord.ui.button(label="Join Giveaway", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.participants:
            self.participants.append(interaction.user)
            await interaction.response.send_message("✅ You entered the giveaway!", ephemeral=True)

@bot.tree.command(name="giveaway")
@app_commands.default_permissions(administrator=True)
async def giveaway(interaction: discord.Interaction, prize: str, duration_minutes: int, giveaway_type: str = "Nitro"):
    await interaction.response.send_message(f"🎉 **{giveaway_type} Giveaway** started!\nPrize: {prize}\nEnds in {duration_minutes} minutes.")
    view = GiveawayView()
    msg = await interaction.channel.send(f"React or click to enter! Winner for **{prize}**", view=view)
    await asyncio.sleep(duration_minutes * 60)
    if view.participants:
        winner = random.choice(view.participants)
        await msg.edit(content=f"🎉 **WINNER**: {winner.mention} won **{prize}**!")
        if "Level" in giveaway_type:
            await winner.add_roles(discord.utils.get(interaction.guild.roles, name="Ultimate Drill King"))  # Example
    else:
        await msg.edit(content="No one entered :(")

bot.run("MTQ4MTcxMDk1NDQ3MDE3ODg0Ng.GnECOT.GhK8Jt-wWwd7JRWhJ4DYJN8QJMpouqe-QwXF24")
