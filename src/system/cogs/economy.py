import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

# Ensure we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.economy.ledger import LedgerManager

class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ledger = LedgerManager()

    @app_commands.command(name="balance", description="Check your SCAR balance (Ephemeral)")
    async def balance(self, interaction: discord.Interaction):
        """Check your SCAR balance."""
        # Defer ephemeral just in case DB is slow, though it should be fast.
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        # Run DB call in thread to avoid blocking
        balance = await self.bot.loop.run_in_executor(None, self.ledger.get_balance, user_id)
        
        embed = discord.Embed(
            title="💰 Vault Balance",
            description=f"**{balance:.4f} SCAR**",
            color=discord.Color.gold()
        )
        embed.set_footer(text="ΔΩ.Holo-Economy")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="pay", description="Transfer SCAR to another user")
    @app_commands.describe(recipient="The user to send SCAR to", amount="Amount of SCAR to transfer")
    async def pay(self, interaction: discord.Interaction, recipient: discord.Member, amount: float):
        """Transfer SCAR to another user."""
        # Defer publically? Or ephemeral first? 
        # "Feedback: Public Embed on success... If Fail: Red Message (Ephemeral)"
        # We can't easily switch from public to ephemeral after deferring.
        # So we will defer ephemeral=True, and if success, send a NEW public message? 
        # Or just defer ephemeral=True for everything?
        # User said: "If Success: Green Embed (Public). If Fail: Red Message (Ephemeral)."
        # Slash commands allow `ephemeral=True` only at the start.
        # If I defer ephemeral, I can't make it public later.
        # If I defer public, I can't make it ephemeral later.
        # Strategy: Defer Ephemeral. If success, send a separate message to the channel (public) and update the ephemeral to say "Sent!".
        
        await interaction.response.defer(ephemeral=True)
        
        sender_id = str(interaction.user.id)
        receiver_id = str(recipient.id)
        
        # Guardrails
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive.", ephemeral=True)
            return
            
        if sender_id == receiver_id:
            await interaction.followup.send("❌ You cannot pay yourself.", ephemeral=True)
            return
            
        if recipient.bot:
            # User said: "if receiver is Bot: Accept (Burn/Donation)"
            pass

        # Execute Transfer (Threaded)
        result = await self.bot.loop.run_in_executor(None, self.ledger.transfer, sender_id, receiver_id, amount)
        
        if result["success"]:
            # 1. Notify Sender (Ephemeral)
            await interaction.followup.send(f"✅ Transfer Complete. New Balance: {result['new_balance']:.4f} SCAR", ephemeral=True)
            
            # 2. Public Announcement (The Teller Window)
            embed = discord.Embed(
                description=f"💸 {interaction.user.mention} sent **{amount:.4f} SCAR** to {recipient.mention}",
                color=discord.Color.green()
            )
            # We use interaction.channel.send to make it public
            if interaction.channel:
                await interaction.channel.send(embed=embed)
        else:
            # Failure (Ephemeral)
            await interaction.followup.send(f"❌ Transfer Failed: {result['message']}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
