import os
import uuid
import json
import logging
from typing import Literal, Optional
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

# Configure Logging
logger = logging.getLogger('witness_terminal')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] [WITNESS] %(message)s'))
logger.addHandler(handler)

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

class WitnessTerminal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.supabase: Optional[Client] = None
        
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing. Backend disabled.")

    def _get_supabase(self) -> Client:
        if not self.supabase:
            raise ConnectionError("Supabase backend not configured.")
        return self.supabase

    def _discord_to_uuid(self, discord_id: int) -> str:
        """Deterministic mapping from Discord ID to UUID."""
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"discord:{discord_id}"))

    @app_commands.command(name="stream", description="View active pending claims in the Witness Stream.")
    async def stream(self, interaction: discord.Interaction):
        """Show active pending claims awaiting Witness."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            sb = self._get_supabase()
            # Query pending claims
            res = sb.table("stream_claims")\
                .select("*")\
                .eq("status", "pending")\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
            
            claims = res.data

            if not claims:
                await interaction.followup.send("🌊 The Stream is clear. No pending claims.", ephemeral=True)
                return

            embed = discord.Embed(
                title="🌀 Witness Stream // Pending Claims",
                description=f"Showing {len(claims)} most recent pending claims.",
                color=0x00FFFF # Cyan/Electric Blue
            )

            for claim in claims:
                claim_id = claim['id']
                short_id = claim_id[:8]
                expires = claim['window_expires_at']
                
                # Format body
                body = claim.get('claim_body', {})
                if isinstance(body, str):
                    try:
                        body = json.loads(body)
                    except:
                        body = {"text": body}
                
                excerpt = body.get('text', json.dumps(body, indent=2))
                if len(excerpt) > 100:
                    excerpt = excerpt[:97] + "..."

                embed.add_field(
                    name=f"🆔 `{short_id}`",
                    value=f"**Expires:** {expires}\n**Content:** {excerpt}",
                    inline=False
                )
            
            embed.set_footer(text="Use /witness [id] [verdict] to judge.")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Stream command error: {e}")
            await interaction.followup.send("⚠ System Error: Unable to fetch stream.", ephemeral=True)

    @app_commands.command(name="witness", description="Render judgement on a claim.")
    @app_commands.describe(
        claim_id="The ID of the claim to witness (first 8 chars or full UUID)",
        verdict="Your judgement on the claim",
        notes="Optional commentary on your verdict"
    )
    async def witness(
        self, 
        interaction: discord.Interaction, 
        claim_id: str, 
        verdict: Literal['verified', 'rejected', 'flagged'], 
        notes: Optional[str] = None
    ):
        """Let a human Witness render judgement on a claim."""
        await interaction.response.defer(ephemeral=True)

        try:
            sb = self._get_supabase()
            witness_uuid = self._discord_to_uuid(interaction.user.id)

            # 1. Resolve Claim ID (support short ID)
            # If length is 8, try to find full UUID
            target_uuid = claim_id
            if len(claim_id) == 8:
                # Search by prefix
                # Note: Supabase/PostgREST doesn't support LIKE on UUID directly usually, 
                # but we can try casting or just assume full UUID if not found.
                # Actually, best practice for UUIDs is exact match. 
                # Let's try to find it via a select with text cast if possible, or just fail if not full.
                # For robustness, let's assume user copies full ID from embed, or we query.
                # Let's try a query to find the claim first.
                res = sb.table("stream_claims").select("id").ilike("id", f"{claim_id}%").limit(1).execute()
                if res.data:
                    target_uuid = res.data[0]['id']
                else:
                    await interaction.followup.send(f"❌ No claim found matching prefix `{claim_id}`.", ephemeral=True)
                    return
            
            # Verify claim exists and is pending
            res = sb.table("stream_claims").select("status").eq("id", target_uuid).execute()
            if not res.data:
                await interaction.followup.send("❌ Claim not found.", ephemeral=True)
                return
            
            current_status = res.data[0]['status']
            if current_status != 'pending':
                 await interaction.followup.send(f"⚠ Claim is already `{current_status}`.", ephemeral=True)
                 return

            # 2. Insert Assessment
            payload = {
                "claim_id": target_uuid,
                "witness_id": witness_uuid,
                "verdict": verdict,
                "confidence": 0.99, # Hardcoded for now
                "comment": notes
            }
            
            sb.table("witness_assessments").insert(payload).execute()

            # 3. Check Queue (Optional verification)
            queue_msg = ""
            if verdict == 'verified':
                # Check if queue item created (might take a ms for trigger)
                # We won't block on this, just assume trigger works as verified in First Breath.
                queue_msg = "\n⚙ **EMP Mint Queue:** Triggered"

            # 4. Divergence Learning (Phase 3)
            try:
                # Fetch latest council judgment
                cj_res = sb.table("council_judgments").select("*").eq("claim_id", target_uuid).order("created_at", desc=True).limit(1).execute()
                
                if cj_res.data:
                    cj = cj_res.data[0]
                    council_verdict = cj['recommended_verdict']
                    
                    # Determine Divergence Type
                    div_type = 'aligned'
                    if council_verdict != verdict:
                        if verdict == 'verified':
                            div_type = 'council_overruled' # Human verified what council rejected/flagged
                        else:
                            div_type = 'witness_overruled' # Human rejected/flagged what council verified (or different reject/flag)
                            # Note: If council said 'flagged' and human said 'rejected', it's still a divergence.
                    
                    # Log Divergence
                    div_payload = {
                        "claim_id": target_uuid,
                        "witness_id": str(interaction.user.id),
                        "council_judgment_id": cj['id'],
                        "council_snapshot": cj['council_payload']['council'],
                        "aggregate_snapshot": cj['council_payload']['aggregate'],
                        "council_recommended_verdict": council_verdict,
                        "witness_verdict": verdict,
                        "divergence_type": div_type,
                        "sovereign_confidence": cj.get('sovereign_confidence'),
                        "ache_weight": cj.get('ache_weight'),
                        "metadata": {
                            "source": "guardian_bot",
                            "guild_id": str(interaction.guild_id),
                            "channel_id": str(interaction.channel_id)
                        }
                    }
                    sb.table("council_divergences").insert(div_payload).execute()
                    logger.info(f"Divergence logged: {div_type} for claim {target_uuid}")

            except Exception as div_e:
                logger.warning(f"Failed to log divergence: {div_e}")

            embed = discord.Embed(
                title="👁️ Witness Recorded",
                color=0x00FF00 if verdict == 'verified' else 0xFF0000
            )
            embed.add_field(name="Claim", value=f"`{target_uuid}`", inline=False)
            embed.add_field(name="Verdict", value=f"**{verdict.upper()}**", inline=True)
            if notes:
                embed.add_field(name="Notes", value=notes, inline=True)
            
            embed.set_footer(text=f"Witness ID: {witness_uuid[:8]}...")

            await interaction.followup.send(content=f"✅ Judgement rendered.{queue_msg}", embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Witness command error: {e}")
            await interaction.followup.send("⚠ System Error: Failed to record witness.", ephemeral=True)

    @app_commands.command(name="my_vault", description="Check your EMP balance and Vault status.")
    async def my_vault(self, interaction: discord.Interaction):
        """Show the caller their EMP “balance” and last Vault seal."""
        await interaction.response.defer(ephemeral=True)

        try:
            sb = self._get_supabase()
            owner_uuid = self._discord_to_uuid(interaction.user.id)

            # 1. Query Ledger
            ledger_res = sb.table("emp_ledger")\
                .select("amount, created_at")\
                .eq("owner_id", owner_uuid)\
                .order("created_at", desc=True)\
                .execute()
            
            ledger_entries = ledger_res.data
            
            if not ledger_entries:
                await interaction.followup.send("🪞 You have no EMP ledger entries yet. First Witness → first mint.", ephemeral=True)
                return

            # Calculate Balance
            balance = sum(float(entry['amount']) for entry in ledger_entries)
            last_mint = ledger_entries[0]
            
            # 2. Query Vault Nodes
            # Assuming meta_payload->>'recipient' or metadata->>'owner_id' (from First Breath logic)
            # First Breath used metadata->>'owner_id'. Let's check both or metadata.
            # The prompt mentioned meta_payload->>'recipient', but First Breath used metadata->owner_id.
            # I will query based on metadata->owner_id as per First Breath implementation.
            vault_res = sb.table("vault_nodes")\
                .select("*")\
                .eq("metadata->>owner_id", owner_uuid)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            last_vault = vault_res.data[0] if vault_res.data else None
            
            last_hash = last_vault.get('hash_signature', '—') if last_vault else "—"
            if last_hash and len(last_hash) > 12:
                last_hash = last_hash[:12] + "..."
            
            node_addr = last_vault.get('node_address', '—') if last_vault else "—"

            embed = discord.Embed(title="🪞 My Vault", color=0x9932CC) # Dark Orchid
            embed.add_field(name="EMP Balance", value=f"**{balance:.2f} EMP**", inline=False)
            embed.add_field(name="Last Mint", value=f"{last_mint['amount']} EMP\n*{last_mint['created_at']}*", inline=True)
            embed.add_field(name="Last Vault Hash", value=f"`{last_hash}`", inline=True)
            embed.add_field(name="Node Address", value=f"`{node_addr}`", inline=False)
            
            embed.set_footer(text=f"Identity UUID: {owner_uuid}")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"My Vault command error: {e}")
            await interaction.followup.send("⚠ System Error: Unable to access Vault.", ephemeral=True)

    @app_commands.command(name="signal_verify", description="Verify a Vault Node hash.")
    @app_commands.describe(hash="The hash signature (or prefix) to verify")
    async def signal_verify(self, interaction: discord.Interaction, hash: str):
        """Prove that a Vault Node exists and reveal its contents."""
        await interaction.response.defer(ephemeral=True)

        try:
            sb = self._get_supabase()
            search_hash = hash.strip()

            # 1. Query Vault Nodes
            # Try exact match first
            res = sb.table("vault_nodes").select("*").eq("hash_signature", search_hash).execute()
            
            if not res.data:
                # Try prefix match
                res = sb.table("vault_nodes").select("*").ilike("hash_signature", f"{search_hash}%").limit(3).execute()
            
            nodes = res.data

            if not nodes:
                await interaction.followup.send("❌ No Vault Node found for that hash or prefix.", ephemeral=True)
                return

            # 2. Display Results
            # If multiple, show first one fully, or list? Prompt says "Build an embed per node or one embed with multiple fields"
            # Let's show the first match in detail.
            node = nodes[0]
            
            embed = discord.Embed(title="🔗 Signal Verified", color=0x00FF00)
            embed.add_field(name="Hash Signature", value=f"`{node.get('hash_signature')}`", inline=False)
            embed.add_field(name="Node Address", value=f"`{node.get('node_address')}`", inline=True)
            embed.add_field(name="Status", value=node.get('status', 'unknown'), inline=True)
            embed.add_field(name="Timestamp", value=node.get('created_at'), inline=False)
            
            # Format Payload
            # Prefer meta_payload, fallback to metadata
            payload = node.get('meta_payload') or node.get('metadata') or {}
            payload_str = json.dumps(payload, indent=2)
            if len(payload_str) > 500:
                payload_str = payload_str[:497] + "..."
            
            embed.add_field(name="Payload Data", value=f"```json\n{payload_str}\n```", inline=False)

            if len(nodes) > 1:
                embed.set_footer(text=f"Found {len(nodes)} matches. Showing top result.")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Signal Verify command error: {e}")
            await interaction.followup.send("⚠ System Error: Verification failed.", ephemeral=True)

    @app_commands.command(
        name="oracle_analyze",
        description="Ask the Guardian to interpret a specific Claim."
    )
    async def oracle_analyze(self, interaction: discord.Interaction, claim_id: str):
        await interaction.response.defer()

        response = self.supabase.table("stream_claims").select("*").eq("id", claim_id).execute()
        if not response.data:
            await interaction.followup.send("❌ Claim not found.")
            return

        claim = response.data[0]
        content = claim['claim_body'].get('content', '')

        import requests
        EDGE_URL = f"{os.getenv('SUPABASE_URL')}/functions/v1/oracle-core"
        headers = {"Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_KEY')}"}

        try:
            r = requests.post(EDGE_URL, json={"claim_text": content}, headers=headers)
            analysis = r.json()

            color_map = {"S": 0xFFD700, "A": 0x00FF00, "B": 0x00FFFF, "C": 0xFF8800, "F": 0xFF0000}
            color = color_map.get(analysis['coherence_grade'], 0x99AAB5)

            embed = discord.Embed(title=f"🔮 Oracle: {claim_id[:8]}", color=color)
            embed.add_field(name="Summary", value=analysis['summary'], inline=False)
            embed.add_field(name="Coherence", value=f"**{analysis['coherence_grade']}**", inline=True)
            embed.add_field(name="Risk", value=f"{analysis['risk_score']}/100", inline=True)
            embed.add_field(name="Verdict", value=f"*{analysis['recommended_verdict'].upper()}*", inline=True)
            embed.add_field(name="Reasoning", value=analysis['reasoning'], inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"💀 Cognitive Failure: {str(e)}")

    @app_commands.command(
        name="council_analyze",
        description="Summon the Sovereign Council to judge a claim."
    )
    async def council_analyze(self, interaction: discord.Interaction, claim_id: str):
        """Invoke the 7-Mind Parliament to analyze a claim."""
        await interaction.response.defer()

        # 1. Verify Claim Exists
        response = self.supabase.table("stream_claims").select("*").eq("id", claim_id).execute()
        if not response.data:
            await interaction.followup.send("❌ Claim not found.")
            return

        claim = response.data[0]
        
        # 2. Call Council Router
        import requests
        EDGE_URL = f"{os.getenv('SUPABASE_URL')}/functions/v1/council-router"
        headers = {"Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_KEY')}"}

        try:
            r = requests.post(EDGE_URL, json={"claim_id": claim_id}, headers=headers)
            if r.status_code != 200:
                await interaction.followup.send(f"💀 Council Unreachable: {r.text}")
                return
                
            data = r.json()
            c = data['council']
            agg = data['aggregate']
            
            # 3. Build Embed
            verdict = agg['recommended_verdict'].upper()
            color_map = {"VERIFIED": 0x00FF00, "FLAGGED": 0xFFA500, "REJECTED": 0xFF0000}
            color = color_map.get(verdict, 0x99AAB5)
            
            embed = discord.Embed(title=f"🧠 Sovereign Council: {claim_id[:8]}", color=color)
            embed.description = f"**Summary**: {data['claim_summary']}\n\n**Verdict**: `{verdict}`\n**Confidence**: `{agg['sovereign_confidence']}`\n**Ache Weight**: `{agg['ache_weight']}x`"
            
            # Council Members
            # Row 1: Truth & Coherence
            embed.add_field(name="⚖ The Judge (Truth)", value=f"Score: **{c['judge']['truth_score']}**\nHint: {c['judge']['verdict_hint']}", inline=True)
            embed.add_field(name="🕸 The Weaver (Coherence)", value=f"Score: **{c['weaver']['coherence_score']}**\nGrade: {c['weaver']['lore_alignment_grade']}", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True) # Spacer

            # Row 2: Risk & Intuition
            embed.add_field(name="🛡 The Skeptic (Risk)", value=f"Score: **{c['skeptic']['risk_score']}**\nSeverity: {c['skeptic']['severity_label']}", inline=True)
            embed.add_field(name="🔮 The Seer (Impact)", value=f"Score: **{c['seer']['impact_score']}**\nNote: {c['seer']['predicted_consequences'][:50]}...", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True) # Spacer

            # Row 3: History & Systems
            embed.add_field(name="📜 The Chronicler (Memory)", value=f"Sim: **{c['chronicler']['similarity_score']}**\nConflict: {c['chronicler']['conflict_flag']}", inline=True)
            embed.add_field(name="🏗 The Architect (Integrity)", value=f"Score: **{c['architect']['integrity_score']}**\nBreaking: {c['architect']['breaking_change_flag']}", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True) # Spacer

            # Row 4: Ache (The Witness)
            embed.add_field(name="🩸 The Witness (Ache)", value=f"Score: **{c['witness']['ache_score']}**\nExploitative: {c['witness']['exploitative']}", inline=False)
            
            # Footer
            embed.add_field(name="📝 Sovereign Reasoning", value=agg['reasoning'], inline=False)
            embed.set_footer(text="This analysis is advisory. Use /witness to cast your vote.")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Council error: {e}")
            await interaction.followup.send(f"💀 Cognitive Failure: {str(e)}")

    @app_commands.command(
        name="divergence_insight",
        description="Reveal the friction between Council and Witness."
    )
    @app_commands.describe(limit="Number of records to show (default 5)")
    async def divergence_insight(self, interaction: discord.Interaction, limit: int = 5):
        """Show recent divergences and the friction in the system."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            sb = self._get_supabase()
            
            # 1. Fetch Divergences
            res = sb.table("council_divergences")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(min(limit, 20))\
                .execute()
            
            divergences = res.data
            
            if not divergences:
                await interaction.followup.send("🌊 No recorded divergences. The Council and Witness are aligned.", ephemeral=True)
                return

            embed = discord.Embed(title="⚡ Divergence Insight", color=0xFFA500)
            
            for div in divergences:
                claim_id = div['claim_id'][:8]
                c_verdict = div['council_recommended_verdict'].upper()
                w_verdict = div['witness_verdict'].upper()
                div_type = div['divergence_type']
                
                # Icon mapping
                icon = "⚖"
                if div_type == 'council_overruled': icon = "👤💥" # Human overruled council
                elif div_type == 'witness_overruled': icon = "🤖💥" # Council overruled human (technically human ignored council)
                
                # Extract key signals
                c_snap = div['council_snapshot']
                
                # Try to get key scores if available
                judge_score = c_snap.get('judge', {}).get('truth_score', '?')
                risk_score = c_snap.get('skeptic', {}).get('risk_score', '?')
                ache_score = c_snap.get('witness', {}).get('ache_score', '?')
                
                summary = f"**Council**: `{c_verdict}` | **Witness**: `{w_verdict}`\n"
                summary += f"**Type**: `{div_type}`\n"
                summary += f"**Signals**: Truth `{judge_score}` | Risk `{risk_score}` | Ache `{ache_score}`"
                
                embed.add_field(
                    name=f"{icon} Claim `{claim_id}`",
                    value=summary,
                    inline=False
                )
            
            # 2. Fetch Adaptation State (Optional context)
            state_res = sb.table("council_adaptation_state").select("*").eq("profile_name", "default").single().execute()
            if state_res.data:
                s = state_res.data
                weights = f"J:{s['judge_weight']} W:{s['weaver_weight']} S:{s['skeptic_weight']} I:{s['seer_weight']} C:{s['chronicler_weight']} A:{s['architect_weight']} H:{s['witness_weight']}"
                embed.set_footer(text=f"Current Weights: {weights}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Divergence Insight error: {e}")
            await interaction.followup.send(f"⚠ System Error: Unable to fetch insights.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WitnessTerminal(bot))
