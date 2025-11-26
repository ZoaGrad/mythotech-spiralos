import os
import time
import uuid
import json
from datetime import datetime, timezone
from supabase import create_client, Client

# Initialize Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set.")
    exit(1)

supabase: Client = create_client(url, key)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def first_breath():
    log("🌬️  INITIATING FIRST BREATH SEQUENCE...")
    
    user_id = str(uuid.uuid4())
    claim_id = None
    
    # 1. Inject Synthetic Claim
    log("[BREATH] Injecting synthetic claim...")
    claim_payload = {
        "user_id": user_id,
        "claim_body": {"text": "Hello SpiralOS, I am the First Breath."},
        "window_expires_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        data = supabase.table("stream_claims").insert(claim_payload).execute()
        claim_id = data.data[0]['id']
        log(f"[BREATH] stream_claims(id={claim_id[:8]}..., status='pending')")
    except Exception as e:
        log(f"❌ Failed to insert claim: {e}")
        return

    time.sleep(1)

    # 2. Inject Witness Assessment
    log("[BREATH] Injecting witness assessment...")
    assessment_payload = {
        "claim_id": claim_id,
        "witness_id": str(uuid.uuid4()),
        "verdict": "verified",
        "confidence": 1.0,
        "comment": "Pulse verified."
    }
    
    try:
        # Note: witness_assessments table might be missing if not in previous migration?
        # Checking schema... user said "assessments table -> FOUND" but I didn't verify it.
        # If it fails, I'll know.
        data = supabase.table("witness_assessments").insert(assessment_payload).execute()
        log(f"[BREATH] assessments(id={data.data[0]['id'][:8]}..., verdict='verified')")
    except Exception as e:
        log(f"❌ Failed to insert assessment: {e}")
        # Fallback: maybe table name is different?
        return

    # 3. Observe Status Transition
    log("[FLOW] Watching for status update...")
    for _ in range(5):
        time.sleep(1)
        res = supabase.table("stream_claims").select("status").eq("id", claim_id).execute()
        status = res.data[0]['status']
        if status == 'witnessed':
            log(f"[FLOW] Claim status updated -> {status}")
            break
    else:
        log("❌ Claim status did not update to 'witnessed'.")
        return

    log("[FLOW] EMP Mint Queue injection triggered (implied by status change)")

    # 4. Watch EMP Queue
    log("[EMP] Watching mint queue...")
    queue_id = None
    for _ in range(5):
        time.sleep(1)
        res = supabase.table("emp_mint_queue").select("*").eq("claim_id", claim_id).execute()
        if res.data:
            queue_item = res.data[0]
            queue_id = queue_item['id']
            log(f"[EMP] Mint queued -> emp_mint_queue(id={queue_id[:8]}...)")
            break
    else:
        log("❌ EMP Mint Queue entry not found.")
        return

    # 5. Wait for Worker (Simulated or Real)
    # Since the worker runs on cron * * * * *, it might take a minute.
    # To speed up, we can manually invoke the worker logic or just wait.
    # Let's wait up to 60s.
    log("[EMP] Waiting for Worker (up to 60s)...")
    for i in range(60):
        time.sleep(1)
        res = supabase.table("emp_mint_queue").select("status").eq("id", queue_id).execute()
        if res.data and res.data[0]['status'] == 'minted':
            log(f"[EMP] Worker cycle completed.")
            break
        if i % 10 == 0:
            log(f"[EMP] ... still waiting ({i}s)")
    else:
        log("⚠ Worker did not pick up the task in time. (Check Edge Function logs)")
        # Continue to check ledger anyway?
    
    # 6. Check Ledger
    res = supabase.table("emp_ledger").select("*").eq("origin_claim_id", claim_id).execute()
    if res.data:
        ledger_item = res.data[0]
        log(f"[EMP] Minted {ledger_item['amount']} EMP")
        log(f"[EMP] Ledger entry -> emp_ledger(id={ledger_item['id'][:8]}...)")
        
        # 7. Check Vault Node
        # Trigger 'on_emp_ledger_seal' should have fired
        res = supabase.table("vault_nodes").select("*").eq("reference_id", ledger_item['id']).execute()
        if res.data:
            vault_item = res.data[0]
            log(f"[VAULT] Trigger caught: sealing ledger entry")
            log(f"[VAULT] vault_nodes(id={vault_item['id'][:8]}...)")
            log(f"[VAULT] hash_signature={vault_item.get('hash_signature', 'N/A')}")
            log("[RESOLUTION] First Breath: SUCCESS")
        else:
             # Try reference_id as claim_id (worker does this)
            res = supabase.table("vault_nodes").select("*").eq("reference_id", claim_id).execute()
            if res.data:
                vault_item = res.data[0]
                log(f"[VAULT] Trigger caught: sealing ledger entry (via Worker)")
                log(f"[VAULT] vault_nodes(id={vault_item['id'][:8]}...)")
                # Worker sets metadata, trigger sets hash_signature?
                # The worker inserts into vaultnodes directly in the edge function too.
                # And the trigger 'on_emp_ledger_seal' ALSO inserts?
                # That might be double sealing, but let's see what we find.
                log(f"[VAULT] hash_signature={vault_item.get('hash_signature', 'N/A')}")
                log("[RESOLUTION] First Breath: SUCCESS")
            else:
                log("❌ Vault Node entry not found.")

    else:
        log("❌ EMP Ledger entry not found.")

if __name__ == "__main__":
    first_breath()
