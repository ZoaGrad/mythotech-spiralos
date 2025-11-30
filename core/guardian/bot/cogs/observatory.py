import discord
from discord.ext import commands
from discord import app_commands
import logging
import datetime

logger = logging.getLogger('guardian.observatory')

class Observatory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = None

    async def cog_load(self):
        self.supabase = getattr(self.bot, 'supabase', None)
        if not self.supabase:
            logger.warning("Supabase client unavailable in Bot.")

    @app_commands.command(name="observatory", description="Access the Sovereign Observatory telemetry.")
    @app_commands.describe(action="Action to perform (status)")
    @app_commands.choices(action=[
        app_commands.Choice(name="status", value="status")
    ])
    async def observatory(self, interaction: discord.Interaction, action: str):
        await interaction.response.defer()
        
        if not self.supabase:
            # Try to fetch again just in case
            self.supabase = getattr(self.bot, 'supabase', None)
        
        if not self.supabase:
            await interaction.followup.send("❌ Database connection unavailable.")
            return

        if action == "status":
            try:
                # Fetch latest telemetry
                res = self.supabase.table("observatory_telemetry").select("*").order("timestamp", desc=True).limit(1).execute()
                
                if not res.data:
                    await interaction.followup.send("🔭 Observatory is still calibrating. No telemetry yet.")
                    return

                telemetry = res.data[0]
                coherence = telemetry['coherence']
                health_state = telemetry['health_state']
                
                # 1. Coherence Bar
                # [███████░░░] 84%
                percent = int(coherence * 100)
                segments = int(percent / 10)
                bar = "█" * segments + "░" * (10 - segments)
                
                # Color based on health
                color = 0x00FF00 # Green
                if health_state == "FRACTURE_DETECTED":
                    color = 0xFF0000 # Red
                elif health_state == "STABLE_FLOW":
                    color = 0x3498DB # Blue

                embed = discord.Embed(
                    title="👁️ Sovereign Observatory",
                    description=f"**System State**: `[{bar}]` **{percent}% COHERENT**\nStatus: **{health_state}**",
                    color=color,
                    timestamp=datetime.datetime.fromisoformat(telemetry['timestamp'].replace("Z", "+00:00"))
                )

                # 2. Council Mood
                # We need to fetch the drift view to determine mood
                # Or we can store "mood" in telemetry metadata in the daemon.
                # For now, let's query the view directly as per prompt instructions.
                try:
                    drift_res = self.supabase.table("view_council_drift").select("*").execute()
                    if drift_res.data:
                        # Find max positive delta
                        max_delta = -1.0
                        dominant_role = "Balanced"
                        for row in drift_res.data:
                            delta = float(row['delta_from_baseline'])
                            if delta > max_delta:
                                max_delta = delta
                                dominant_role = row['role']
                        
                        mood_text = "BALANCED"
                        if max_delta > 0.05: # Threshold
                            mood_map = {
                                "judge": "JUDGMENTAL (Truth focus)",
                                "weaver": "MYTHIC (Lore focus)",
                                "skeptic": "PARANOID (Risk focus)",
                                "seer": "VISIONARY (Future focus)",
                                "chronicler": "NOSTALGIC (History focus)",
                                "architect": "STRUCTURAL (System focus)",
                                "witness": "MERCIFUL (Human focus)"
                            }
                            mood_text = mood_map.get(dominant_role, dominant_role.upper())
                        
                        embed.add_field(name="🧠 Council Mood", value=f"**{mood_text}**", inline=True)
                except Exception as e:
                    logger.error(f"Failed to fetch council mood: {e}")

                # 3. Economy Status
                vel_minted = telemetry['velocity_minted']
                # Simple heuristic
                econ_status = "STAGNANT"
                if vel_minted > 150:
                    econ_status = "OVERHEATING"
                elif vel_minted > 50:
                    econ_status = "FLOWING"
                elif vel_minted > 10:
                    econ_status = "COOLING"
                
                embed.add_field(name="💎 Economy", value=f"**{econ_status}**\n({int(vel_minted)} EMP/day)", inline=True)

                # 4. Next Divergence Check
                # Cron is 03:00 UTC.
                now = datetime.datetime.now(datetime.timezone.utc)
                target = now.replace(hour=3, minute=0, second=0, microsecond=0)
                if now >= target:
                    target += datetime.timedelta(days=1)
                
                ts = int(target.timestamp())
                embed.add_field(name="⏳ Next Reflection", value=f"<t:{ts}:R>", inline=False)

                if health_state == "FRACTURE_DETECTED":
                    embed.add_field(name="🚨 WARNING", value="Cognitive Fracture Detected. Immediate remediation required.", inline=False)

                embed.set_footer(text="Sovereign Observatory // Telemetry Node")
                await interaction.followup.send(embed=embed)

            except Exception as e:
                logger.error(f"Error in observatory status: {e}")
                await interaction.followup.send(f"❌ Error fetching status: {e}")

async def setup(bot):
    await bot.add_cog(Observatory(bot))
