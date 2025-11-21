import discord
from discord.ext import commands
import os
import asyncio
from supabase import create_client

# ΔΩ: LENS CONFIGURATION
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

@bot.event
async def on_ready():
    print(f">> [LENS] ONLINE. Identity: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Lattice"))

@bot.command(name="status")
async def status(ctx):
    try:
        sb = get_supabase()
        response = sb.table("attestations").select("*").order("created_at", desc=True).limit(1).execute()
        if response.data:
            latest = response.data[0]
            wi = float(latest.get("final_wi_score", 0.0))
            color = 0xFFD700 if wi > 1.0 else 0x3498DB
            
            embed = discord.Embed(title="ΔΩ.SYSTEM_STATUS // ONLINE", color=color)
            embed.add_field(name="Current WI Energy", value=f"`{wi:.4f}` J", inline=True)
            embed.add_field(name="Latest Pulse", value=latest.get("description", "Unknown"), inline=False)
            embed.set_footer(text=f"Logged: {latest.get('created_at')}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(">> [LENS] LEDGER EMPTY.")
    except Exception as e:
        await ctx.send(f"ERROR: {e}")

async def start_guardian():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        async with bot:
            await bot.start(token)
    else:
        print(">> [LENS] NO TOKEN FOUND.")
