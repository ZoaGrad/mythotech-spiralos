import os
import sys
import unittest
from unittest.mock import MagicMock

# Set required environment variables for the bot to start
os.environ["GUARDIAN_EDGE_URL"] = "https://mock-edge-url.com"
os.environ["DISCORD_GUARDIAN_WEBHOOK"] = "https://mock-webhook-url.com"
os.environ["DISCORD_CHANNEL_ID"] = "123456789"
os.environ["DISCORD_GUILD_ID"] = "987654321"
os.environ["DISCORD_BOT_TOKEN"] = "mock-token"
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock-key"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the bot class
from core.guardian.bot.guardian_bot import GuardianBot, bot

# Mock the run method to avoid actual connection but trigger on_ready logic if possible
# Since discord.py run() blocks and connects, we can't easily trigger on_ready without a real token.
# However, we can manually call on_ready() to test the protocol logic!

import asyncio

async def manual_awakening():
    print("[INIT] Manually triggering Guardian Awakening Protocol...")
    
    # Mock the bot's internal state
    with unittest.mock.patch.object(GuardianBot, 'user', new_callable=unittest.mock.PropertyMock) as mock_user, \
         unittest.mock.patch.object(GuardianBot, 'guilds', new_callable=unittest.mock.PropertyMock) as mock_guilds:
        mock_user.return_value = "Guardian#1234"
        mock_guilds.return_value = [MagicMock()]
        
        # Mock the Witness Cog and Supabase
        witness_cog = MagicMock()
        bot.get_cog = MagicMock(return_value=witness_cog)
        
        # Mock Supabase Client in Cog
        mock_sb = MagicMock()
        witness_cog.supabase = mock_sb
        
        # Mock Supabase Responses
        # 1. Connection
        mock_sb.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()
        
        # 2. Signal Verify
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            'hash_signature': 'b9cf4143b58922e1e55a157b8e918041'
        }]
        
        # 4. VaultNode Lookup
        mock_sb.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()
        
        # Mock Channel for Heartbeat
        mock_channel = MagicMock()
        
        # Since we are calling async method, we need async mocks if they are awaited
        async def async_send(*args, **kwargs):
            print(f"[MOCK DISCORD] Sent: {args[0]}")
            return
        
        mock_channel.send = async_send
        bot.get_channel = MagicMock(return_value=mock_channel)
        
        # Execute the protocol
        await bot.on_ready()

if __name__ == "__main__":
    asyncio.run(manual_awakening())
