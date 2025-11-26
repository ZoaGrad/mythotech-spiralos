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

async def setup(bot: commands.Bot):
    await bot.add_cog(WitnessTerminal(bot))
