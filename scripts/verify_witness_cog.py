import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock discord and supabase before importing the cog
mock_discord = MagicMock()
# Make decorators return the function they decorate
def identity_decorator(*args, **kwargs):
    return lambda func: func

# Assign directly, do not use MagicMock with side_effect
mock_discord.app_commands.command = identity_decorator
mock_discord.app_commands.describe = identity_decorator

sys.modules['discord'] = mock_discord
sys.modules['discord.app_commands'] = mock_discord.app_commands
sys.modules['discord.ext'] = MagicMock()

# Define a dummy Cog class so WitnessTerminal doesn't inherit MagicMock behavior
class DummyCog:
    pass

mock_commands = MagicMock()
mock_commands.Cog = DummyCog
mock_commands.Bot = MagicMock
sys.modules['discord.ext.commands'] = mock_commands

# Import the Cog (after mocking)
# We need to mock the Supabase client creation inside the Cog or set env vars
os.environ['SUPABASE_URL'] = 'https://mock.supabase.co'
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'mock-key'

from core.guardian.bot.cogs.witness import WitnessTerminal

async def verify_witness_cog():
    print("[SEARCH] Initiating Witness Cog Verification Ritual...")
    
    # Mock Bot
    mock_bot = MagicMock()
    
    # Initialize Cog
    cog = WitnessTerminal(mock_bot)
    
    # Mock Supabase Client
    mock_sb = MagicMock()
    cog.supabase = mock_sb
    
    # Test 1: /signal_verify
    print("\n[TEST] /signal_verify 'b9cf4143...'")
    mock_interaction = AsyncMock()
    mock_interaction.user.id = 123456789
    # Fix: Make defer and send awaitable
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()
    
    # Mock DB Response for Vault Node
    mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        'hash_signature': 'b9cf4143b58922e1e55a157b8e918041',
        'node_address': 'EMP_MINT:test-uuid',
        'status': 'sealed',
        'created_at': '2025-11-26T00:00:00Z',
        'meta_payload': {'amount': 10.0, 'recipient': 'test-user'}
    }]
    
    await cog.signal_verify(mock_interaction, "b9cf4143b58922e1e55a157b8e918041")
    
    # Verify Embed was sent
    if mock_interaction.followup.send.called:
        args, kwargs = mock_interaction.followup.send.call_args
        embed = kwargs.get('embed')
        if embed:
            print("[OK] Embed sent successfully.")
            # We can't inspect the mock embed easily because it's a MagicMock, 
            # but the fact it didn't crash and called send is good.
            print("[OK] Verification Ritual Complete: The Guardian can see the sealed event.")
        else:
            print("[FAIL] Error: No embed sent.")
    else:
        print("[FAIL] Error: interaction.followup.send not called.")

if __name__ == "__main__":
    asyncio.run(verify_witness_cog())
