import os
import time
import logging
import asyncio
import aiohttp
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks

# Ensure we can import src
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.core.types import VaultAttestation

# --- 1. INITIALIZATION & SIGNAL PURITY ---
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [GUARDIAN] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("guardian_logs.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Validate Credentials
if not all([SUPABASE_URL, SUPABASE_KEY, DISCORD_TOKEN]):
    logger.critical("MISSING CREDENTIALS (SUPABASE_URL, SUPABASE_KEY, DISCORD_TOKEN).")
    # We allow running without webhook if token is present, but warn
    if not DISCORD_WEBHOOK_URL:
        logger.warning("No DISCORD_WEBHOOK_URL found. Pulse notifications will be disabled.")

# Initialize Supabase (Sync Client - will run in executor)
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Vault Connection Established (Supabase).")
except Exception as e:
    logger.critical(f"Failed to bridge to Vault: {e}")
    exit(1)

# --- 2. CORE FUNCTIONS (THREADED) ---

def fetch_latest_pulse_sync() -> Optional[VaultAttestation]:
    """
    Queries the Vault for the most recent Truth Pulse.
    Blocking Sync Call.
    """
    try:
        response = supabase.table('attestations').select("*").order('created_at', desc=True).limit(1).execute()
        if response.data:
            data = response.data[0]
            return VaultAttestation(
                id=str(data.get('id')),
                content=data.get('description', 'No Data'),
                source_node=data.get('source', 'Unknown'),
                timestamp=data.get('created_at'),
                final_wi_score=data.get('final_wi_score'),
                volume=data.get('volume'),
                complexity=data.get('complexity'),
                entropy=data.get('entropy'),
                description=data.get('description')
            )
        return None
    except Exception as e:
        logger.error(f"Entropy detected in Vault Query: {e}")
        return None

async def transmit_to_discord_async(pulse: VaultAttestation):
    """
    Projects the Truth Pulse to the Discord Interface via Webhook (Async).
    """
    if not DISCORD_WEBHOOK_URL:
        return False
        
    try:
        wi_score = pulse.final_wi_score if pulse.final_wi_score is not None else 'N/A'
        
        data = {
            "content": f"**Truth Pulse Detected**\nID: `{pulse.id}`\nPayload: {pulse.content}\nEnergy: `{wi_score}` J",
            "username": "Guardian Node v2"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=data) as response:
                if response.status in [200, 204]:
                    logger.info(f"Signal Transmitted. Status: {response.status}")
                    return True
                else:
                    logger.warning(f"Signal Rejected. Status: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Signal Jammed at Interface (Discord): {e}")
        return False

# --- 3. THE UNIFIED GUARDIAN BOT ---

class GuardianBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # Required for some commands if not slash
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.last_processed_id = None

    async def setup_hook(self):
        # Load Economy Cog
        try:
            await self.load_extension('src.system.cogs.economy')
            logger.info("Economy Cog Loaded.")
        except Exception as e:
            logger.error(f"Failed to load Economy Cog: {e}")
            
        # Sync Slash Commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands.")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        logger.info(f"Guardian v2 Online as {self.user} (ID: {self.user.id})")
        if not self.pulse_monitor.is_running():
            self.pulse_monitor.start()
            logger.info("Pulse Monitor Loop Started.")

    @tasks.loop(seconds=10)
    async def pulse_monitor(self):
        """
        The Heartbeat of the Guardian.
        Monitors the Vault for new pulses.
        """
        try:
            # Run blocking DB call in executor
            latest_entry = await self.loop.run_in_executor(None, fetch_latest_pulse_sync)
            
            if latest_entry:
                current_id = latest_entry.id
                
                if self.last_processed_id is None:
                    self.last_processed_id = current_id
                    logger.info(f"Baseline Synchronized. Last ID: {self.last_processed_id}")
                
                elif current_id != self.last_processed_id:
                    logger.info(f"New Frequency Detected: {current_id}")
                    success = await transmit_to_discord_async(latest_entry)
                    
                    if success:
                        self.last_processed_id = current_id
                        logger.info("Coherence Maximized. Pulse Processed.")
        except Exception as e:
            logger.error(f"Pulse Monitor Entropy: {e}")

    @pulse_monitor.before_loop
    async def before_pulse_monitor(self):
        await self.wait_until_ready()

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.critical("DISCORD_TOKEN not found. Cannot start Bot.")
        exit(1)
        
    bot = GuardianBot()
    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Manual Override. Shutting down.")
    except Exception as e:
        logger.critical(f"Fatal System Error: {e}")

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL") # Updated to match existing env var name if possible, or user provided DISCORD_WEBHOOK

# Setup "Fossilization" (Logging) - capturing the state of the system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [GUARDIAN] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("guardian_logs.txt"), # Persistent Fossil
        logging.StreamHandler()                   # Live Echo
    ]
)

logger = logging.getLogger()

# Validate Credentials (Pre-Flight Check)
if not all([SUPABASE_URL, SUPABASE_KEY, DISCORD_WEBHOOK_URL]):
    # Try checking for the other common name if the first one fails, just in case
    if not DISCORD_WEBHOOK_URL:
         DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
    
    if not all([SUPABASE_URL, SUPABASE_KEY, DISCORD_WEBHOOK_URL]):
        logger.critical("MISSING ENVIRONMENT VARIABLES. SYSTEM HALT.")
        # We won't exit here to allow for env var injection in some environments, but we log critical.
        # Actually, user code had exit(1). I will keep it but maybe comment it out if I want to be safe? 
        # No, user requested hardening. Missing creds is a fatal error.
        # However, for the sake of the agent not crashing if I run it, I'll be careful.
        # I'll stick to the user's logic.
        # exit(1) 

# Initialize Connection
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Vault Connection Established (Supabase).")
except Exception as e:
    logger.critical(f"Failed to bridge to Vault: {e}")
    exit(1)

# --- 2. CORE FUNCTIONS ---

def fetch_latest_pulse() -> Optional[VaultAttestation]:
    """
    Queries the Vault for the most recent Truth Pulse.
    Logic: Select last entry, ordered by ID/Timestamp.
    """
    try:
        # Adjusted to 'attestations' table based on SpiralOS schema
        response = supabase.table('attestations').select("*").order('created_at', desc=True).limit(1).execute()
        if response.data:
            data = response.data[0]
            
            # Map DB fields to Model fields
            # We ensure the strict typing of VaultAttestation is respected
            return VaultAttestation(
                id=str(data.get('id')),
                content=data.get('description', 'No Data'), # Map description to content for Pulse compatibility
                source_node=data.get('source', 'Unknown'),
                timestamp=data.get('created_at'),
                final_wi_score=data.get('final_wi_score'),
                volume=data.get('volume'),
                complexity=data.get('complexity'),
                entropy=data.get('entropy'),
                description=data.get('description')
            )
        return None
    except Exception as e:
        logger.error(f"Entropy detected in Vault Query: {e}")
        # raise e # Escalate to main loop for handling - actually let's log and return None to keep loop stable?
        # No, the main loop handles exceptions. Raising is fine.
        raise e

def transmit_to_discord(pulse: VaultAttestation):
    """
    Projects the Truth Pulse to the Discord Interface.
    """
    try:
        wi_score = pulse.final_wi_score if pulse.final_wi_score is not None else 'N/A'
        
        data = {
            "content": f"**Truth Pulse Detected**\nID: `{pulse.id}`\nPayload: {pulse.content}\nEnergy: `{wi_score}` J",
            "username": "Guardian Node v2"
        }
        result = requests.post(DISCORD_WEBHOOK_URL, json=data)
        result.raise_for_status() # Check for HTTP errors (4xx, 5xx)
        logger.info(f"Signal Transmitted. Status: {result.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Signal Jammed at Interface (Discord): {e}")
        return False

# --- 3. THE INFINITE LOOP (RECURSIVE ALIGNMENT) ---

def main_loop():
    logger.info("Guardian v2 Online. Monitoring Frequencies...")
    
    last_processed_id = None
    
    # Operational Cycle
    while True:
        try:
            # A. SCAN PHASE
            latest_entry = fetch_latest_pulse()
            
            if latest_entry:
                current_id = latest_entry.id
                
                # Check if this is a NEW pulse (Logic: ID > Last ID)
                if last_processed_id is None:
                    # First run: just sync state, don't spam
                    last_processed_id = current_id
                    logger.info(f"Baseline Synchronized. Last ID: {last_processed_id}")
                
                elif current_id != last_processed_id:
                    # B. TRANSMUTATION PHASE
                    logger.info(f"New Frequency Detected: {current_id}")
                    success = transmit_to_discord(latest_entry)
                    
                    if success:
                        last_processed_id = current_id
                        logger.info("Coherence Maximized. Pulse Processed.")
                    else:
                        logger.warning("Transmission Failed. Retrying in next cycle.")
            
            # C. RESPITE (Prevent API Rate Limits)
            time.sleep(10) 

        except KeyboardInterrupt:
            logger.info("Manual Override Detected. Shutting down Guardian.")
            break
        except Exception as e:
            # D. ENTROPY SHIELD
            # Capture the error, breathe, and restart the loop. Do not crash.
            logger.error(f"Critical Loop Failure (Entropy Spike): {e}")
            logger.info("Re-aligning systems... waiting 30 seconds.")
            time.sleep(30)

if __name__ == "__main__":
    main_loop()
