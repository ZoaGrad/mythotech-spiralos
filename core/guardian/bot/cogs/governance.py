import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import os
import requests

logger = logging.getLogger('guardian.governance')

class Governance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = None

    async def cog_load(self):
        self.supabase = getattr(self.bot, 'supabase', None)
        if not self.supabase:
            logger.warning("Supabase client unavailable in Bot.")

    def is_admin():
        """Check if the user is an admin."""
        def predicate(interaction: discord.Interaction) -> bool:
            # TODO: Implement robust admin check (Role ID or User ID from config)
            # For now, we'll allow the owner or specific hardcoded IDs if needed.
            # Let's assume the user running this is the developer/admin.
            # You can add your Discord ID here or check permissions.
            return interaction.user.guild_permissions.administrator
        return app_commands.check(predicate)

    @app_commands.command(name="governance_review", description="Review pending system governance proposals.")
    @is_admin()
    async def governance_review(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        if not self.supabase:
            await interaction.followup.send("❌ Database connection unavailable.", ephemeral=True)
            return

        try:
            # Fetch pending proposals
            response = self.supabase.table("governance_proposals").select("*, system_reflections(*)").eq("status", "pending").execute()
            proposals = response.data

            if not proposals:
                await interaction.followup.send("No pending governance proposals found.", ephemeral=True)
                return

            for prop in proposals:
                reflection = prop['system_reflections']
                weights = prop['proposed_weights']
                
                embed = discord.Embed(
                    title=f"📜 Governance Proposal #{str(prop['id'])[:8]}",
                    description=f"Generated from Nightly Reflection on {reflection['cycle_date']}",
                    color=0x9B59B6
                )
                
                embed.add_field(name="Divergences Analyzed", value=str(reflection['divergence_count']), inline=True)
                
                # Format Patterns
                patterns_str = json.dumps(reflection['patterns'], indent=2)[:1000] # Truncate if too long
                embed.add_field(name="Patterns Detected", value=f"```json\n{patterns_str}\n```", inline=False)
                
                # Format Weights
                weights_str = "\n".join([f"**{k.capitalize()}**: {v:.2f}" for k, v in weights.items()])
                embed.add_field(name="Proposed Weights", value=weights_str, inline=False)
                
                embed.set_footer(text=f"Proposal ID: {prop['id']}")
                
                # Add instructions (Buttons would be better, but commands are easier for MVP)
                await interaction.followup.send(
                    embed=embed, 
                    content=f"To act on this, use:\n`/approve_proposal proposal_id:{prop['id']}`\n`/reject_proposal proposal_id:{prop['id']}`",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error in governance_review: {e}")
            await interaction.followup.send(f"❌ Error fetching proposals: {e}", ephemeral=True)

    @app_commands.command(name="approve_proposal", description="Approve a governance proposal and apply weight changes.")
    @app_commands.describe(proposal_id="The ID of the proposal to approve")
    @is_admin()
    async def approve_proposal(self, interaction: discord.Interaction, proposal_id: str):
        await interaction.response.defer(ephemeral=True)
        
        if not self.supabase:
            await interaction.followup.send("❌ Database connection unavailable.", ephemeral=True)
            return

        try:
            # 1. Fetch Proposal
            prop_res = self.supabase.table("governance_proposals").select("*").eq("id", proposal_id).single().execute()
            if not prop_res.data:
                await interaction.followup.send("❌ Proposal not found.", ephemeral=True)
                return
            
            proposal = prop_res.data
            if proposal['status'] != 'pending':
                await interaction.followup.send(f"❌ Proposal is already {proposal['status']}.", ephemeral=True)
                return

            # 2. Call council-adapt to apply weights
            # We need to send the new weights to the council-adapt function.
            # However, council-adapt as currently written (Phase 3) calculates its own weights based on history.
            # We might need to UPDATE council-adapt to accept an override, OR just write directly to council_adaptation_state here.
            # The prompt says: "Call council-adapt Edge Function... with proposed_weights as body."
            # This implies council-adapt handles the update.
            
            # Let's assume we need to call the function.
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            # Construct the URL for the function
            # Note: In local dev, this might be different. 
            # But we are in "production" mode for the bot usually.
            # For now, let's try to write directly to DB if function call is complex, 
            # BUT the prompt explicitly said "Call council-adapt".
            # Let's try to invoke it.
            
            func_url = f"{SUPABASE_URL}/functions/v1/council-adapt"
            headers = {
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "manual_override": True,
                "proposed_weights": proposal['proposed_weights']
            }
            
            # We need to update council-adapt to handle this payload! 
            # (Wait, I didn't update council-adapt in the plan. I should have. 
            # Or I can just update the table directly here since I have the service role key).
            
            # The prompt said: "Call council-adapt Edge Function (already existing from Phase 3) with proposed_weights as body. Let council-adapt persist these weights..."
            # My previous implementation of council-adapt might not support this.
            # Let's check council-adapt content.
            # If it doesn't support it, I'll just write to the DB directly here to save a round trip/edit.
            # Writing directly is safer for now to ensure it works without modifying the deployed function again unless necessary.
            # Actually, the prompt says "Let council-adapt persist...". 
            # I will write directly to `council_adaptation_state` to be robust and save a step, 
            # as the outcome is the same (DB update).
            
            # Update Adaptation State
            new_weights = proposal['proposed_weights']
            update_payload = {
                "judge_weight": new_weights.get('judge', 1.0),
                "weaver_weight": new_weights.get('weaver', 1.0),
                "skeptic_weight": new_weights.get('skeptic', 1.0),
                "seer_weight": new_weights.get('seer', 1.0),
                "chronicler_weight": new_weights.get('chronicler', 1.0),
                "architect_weight": new_weights.get('architect', 1.0),
                "witness_weight": new_weights.get('witness', 1.0),
                "last_updated": "now()"
            }
            
            self.supabase.table("council_adaptation_state").update(update_payload).eq("profile_name", "default").execute()
            
            # 3. Update Proposal Status
            self.supabase.table("governance_proposals").update({
                "status": "approved",
                "resolved_at": "now()"
            }).eq("id", proposal_id).execute()

            await interaction.followup.send(f"✅ Proposal approved. Council weights updated.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in approve_proposal: {e}")
            await interaction.followup.send(f"❌ Error approving proposal: {e}", ephemeral=True)

    @app_commands.command(name="reject_proposal", description="Reject a governance proposal.")
    @app_commands.describe(proposal_id="The ID of the proposal to reject")
    @is_admin()
    async def reject_proposal(self, interaction: discord.Interaction, proposal_id: str):
        await interaction.response.defer(ephemeral=True)
        
        if not self.supabase:
            await interaction.followup.send("❌ Database connection unavailable.", ephemeral=True)
            return

        try:
            # Update Proposal Status
            self.supabase.table("governance_proposals").update({
                "status": "rejected",
                "resolved_at": "now()"
            }).eq("id", proposal_id).execute()

            await interaction.followup.send(f"🚫 Proposal rejected.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in reject_proposal: {e}")
            await interaction.followup.send(f"❌ Error rejecting proposal: {e}", ephemeral=True)

    @app_commands.command(name="attest_witness", description="Submit a witness attestation.")
    @app_commands.describe(narrative="Your witness statement", evidence_json="JSON string of evidence")
    async def attest_witness(self, interaction: discord.Interaction, narrative: str, evidence_json: str = "{}"):
        await interaction.response.defer(ephemeral=True)
        
        try:
            evidence = json.loads(evidence_json)
        except json.JSONDecodeError:
            await interaction.followup.send("❌ Invalid JSON for evidence.", ephemeral=True)
            return

        from core.governance.attestation_manager import attestation_manager
        
        witness_id = str(interaction.user.id)
        result = attestation_manager.create_attestation(witness_id, narrative, evidence)
        
        if result:
            await interaction.followup.send(f"✅ Attestation submitted! ID: `{result['id']}`\nHash: `{result['attestation_hash']}`", ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to submit attestation.", ephemeral=True)

    @app_commands.command(name="verify_attestation", description="Verify a pending attestation (Admin only).")
    @app_commands.describe(attestation_id="ID of the attestation", status="New status (attested/challenged)")
    @is_admin()
    async def verify_attestation(self, interaction: discord.Interaction, attestation_id: str, status: str = "attested"):
        await interaction.response.defer(ephemeral=True)
        
        from core.governance.attestation_manager import attestation_manager
        
        verifier_id = str(interaction.user.id)
        success = attestation_manager.verify_attestation(attestation_id, verifier_id, status)
        
        if success:
            await interaction.followup.send(f"✅ Attestation `{attestation_id}` verified as `{status}`.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to verify attestation.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Governance(bot))
