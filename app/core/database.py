import logging
from supabase import create_client, Client
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def verify_connection(self) -> bool:
        """
        Runs a lightweight query to prove the client is active.
        """
        try:
            # Running a lightweight query.
            # We attempt to count rows in 'constitutional_execution_log' as requested.
            # We use 'head=True' to avoid fetching data, just the count or check existence.
            self.client.table("constitutional_execution_log").select("*", count="exact", head=True).execute()

            logger.info("✅ SIGNAL CLEAR: Memory Core Integrated")
            return True
        except Exception as e:
            logger.error(f"❌ SIGNAL LOST: Entity is ghosting. Error: {str(e)}")
            return False
