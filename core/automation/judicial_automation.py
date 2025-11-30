"""
JudicialAutomation - The Automated Hand of the F2 Judges
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.db import get_supabase
from core.panic_frames import get_panic_manager, PanicStatus

logger = logging.getLogger("governance.judicial_automation")

class JudicialAutomation:
    def __init__(self):
        self.supabase = get_supabase()
        self.panic_manager = get_panic_manager()

    def check_and_execute(self):
        """
        Main loop to check for conditions requiring judicial intervention.
        1. Check active Panic Frames -> Freeze Operations
        2. Check Coherence Anomalies -> Flag for Review
        """
        self._enforce_panic_protocols()
        # self._review_anomalies() # Future expansion

    def _enforce_panic_protocols(self):
        """
        If a Panic Frame is active, ensure operations are frozen and log a Judicial Action.
        """
        active_frames = self.panic_manager.get_active_frames()
        
        for frame in active_frames:
            # Check if we've already logged a judicial action for this frame
            existing_action = self.supabase.table("judicial_actions") \
                .select("id") \
                .eq("trigger_event_id", frame.id) \
                .eq("action_type", "freeze_operations") \
                .execute()
            
            if not existing_action.data:
                # No action recorded yet, execute freeze and log it
                logger.warning(f"Executing Judicial Freeze for Panic Frame {frame.id}")
                
                # The PanicManager handles the actual "freezing" logic internally (state flags),
                # but here we formalize it as a governance action.
                
                action_id = self._log_judicial_action(
                    action_type="freeze_operations",
                    trigger_event_id=frame.id,
                    executor_id="System_Automator",
                    justification=f"Panic Frame {frame.id} active. ScarIndex: {frame.scarindex_value}",
                    metadata={"frozen_operations": [op.value for op in frame.actions_frozen]}
                )
                
                if action_id:
                    logger.info(f"Judicial Action {action_id} recorded.")

    def _log_judicial_action(self, action_type: str, trigger_event_id: str, executor_id: str, justification: str, metadata: Dict) -> Optional[str]:
        """Log an action to the judicial_actions table."""
        try:
            payload = {
                "action_type": action_type,
                "trigger_event_id": trigger_event_id,
                "executor_id": executor_id,
                "justification": justification,
                "metadata": metadata,
                "status": "executed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            res = self.supabase.table("judicial_actions").insert(payload).execute()
            if res.data:
                return res.data[0]['id']
            return None
        except Exception as e:
            logger.error(f"Failed to log judicial action: {e}")
            return None

# Singleton
judicial_automator = JudicialAutomation()
