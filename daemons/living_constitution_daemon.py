"""
Living Constitution Daemon (ΔΩ.150.5)
The heartbeat of the Three-Branch Governance System.
"""
import time
import logging
import os
from core.coherence_loop import run_coherence_cycle
from core.automation.judicial_automation import judicial_automator
from core.governance.attestation_manager import attestation_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("daemon.living_constitution")

def run_governance_cycle():
    """
    Executes one full governance cycle:
    1. Coherence: Run Coherence Loop (Sensing)
    2. Judicial: Run Judicial Automation (Enforcement)
    3. Legislative: Check for pending attestations (Validation)
    """
    logger.info("Starting Governance Cycle...")
    
    # 1. Coherence Loop
    try:
        run_coherence_cycle()
    except Exception as e:
        logger.error(f"Coherence Loop failed: {e}")

    # 2. Judicial Automation
    try:
        judicial_automator.check_and_execute()
    except Exception as e:
        logger.error(f"Judicial Automation failed: {e}")

    # 3. Attestation Check (Legislative/Witnessing)
    try:
        pending = attestation_manager.get_pending_attestations()
        if pending:
            logger.info(f"Pending Attestations: {len(pending)}")
            # In a real daemon, we might alert Discord here or just log
    except Exception as e:
        logger.error(f"Attestation check failed: {e}")

    logger.info("Governance Cycle Complete.")

if __name__ == "__main__":
    logger.info("Living Constitution Daemon Initialized.")
    
    # In a real deployment, this would loop forever with sleep
    # For verification, we run once
    run_governance_cycle()
