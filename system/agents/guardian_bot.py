import discord
from discord.ext import commands
import os
import asyncio
from supabase import create_client
from holoeconomy.wi.compute_wi import calculate_wi

# ΔΩ: GUARDIAN CONFIGURATION
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

@bot.command(name="log")
async def log_work(ctx, volume: int, complexity: float, *, description: str):
    """
    ΔΩ: MANUAL INJECTION
    Usage: !log [volume] [complexity] [description]
    """
    print(f">> [LENS] LOG REQUEST: Vol={volume} Cpx={complexity} Desc={description}")
    
    try:
        # 1. Calculate Thermodynamics
        final_wi = calculate_wi(volume, complexity, 0.1)
        
        # 2. Inscribe to Ledger
        sb = get_supabase()
        data = {
            "volume": volume,
            "complexity": complexity,
            "entropy": 0.1,
            "source": "discord_manual",
            "description": f"[MANUAL] {description}",
            "final_wi_score": final_wi
        }
        
        sb.table("attestations").insert(data).execute()
        
        # 3. Report to Architect
        embed = discord.Embed(title="ΔΩ.LEDGER_UPDATE // MANUAL", color=0x9B59B6)
        embed.add_field(name="Energy Captured", value=f"`{final_wi:.4f}` J", inline=True)
        embed.add_field(name="Entry", value=description, inline=False)
        embed.set_footer(text=f"Logged by {ctx.author.name}")
        
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"**INJECTION FAILED:** {str(e)}")

async def start_guardian():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        async with bot:
            await bot.start(token)
    else:
        print(">> [LENS] NO TOKEN FOUND.")
