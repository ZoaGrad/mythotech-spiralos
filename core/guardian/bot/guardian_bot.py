#!/usr/bin/env python3
"""
SpiralOS Guardian Bot - Enhanced Discord Integration
Provides rich embeds, interactive commands, and advanced alerting.
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks


@dataclass
class GuardianMetrics:
    """Container for Guardian system metrics."""

    timestamp: str
    window_hours: int
    vault_nodes: int
    ache_events: int
    scarindex_avg: Optional[float]
    scarindex_latest: Optional[float]
    alerts_24h: int
    scar_status: str
    scar_score: Optional[float]
    coherence_components: Optional[Dict[str, float]] = None
    pid_state: Optional[Dict[str, float]] = None
    panic_frames: Optional[int] = None


class GuardianBot(commands.Bot):
    """Enhanced SpiralOS Guardian Discord Bot."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents, description="SpiralOS Guardian - System Health Monitor")

        self.edge_url = os.getenv("GUARDIAN_EDGE_URL")
        self.api_url = os.getenv("GUARDIAN_API_URL") or self.edge_url
        self.webhook_url = os.getenv("DISCORD_GUARDIAN_WEBHOOK")
        self.channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID", "0"))

        if not self.edge_url:
            raise ValueError("GUARDIAN_EDGE_URL environment variable is required")

    async def setup_hook(self):
        """Initialize bot and sync commands."""
        # Load extensions
        try:
            await self.load_extension("cogs.witness")
            print("✅ Loaded extension: cogs.witness")
        except Exception as e:
            print(f"❌ Failed to load extension cogs.witness: {e}")

        # Sync commands to guild for faster updates during development
        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

        # Start periodic heartbeat
        self.heartbeat_task.start()

    async def on_ready(self):
        """Called when bot is ready."""
        print(f"✅ Guardian Bot logged in as {self.user}")
        print(f"   Connected to {len(self.guilds)} guild(s)")
        print(f"   Monitoring channel: {self.channel_id}")

    async def fetch_guardian_status(self, hours: int = 24) -> GuardianMetrics:
        """Fetch status from Guardian Edge Function."""
        url = f"{self.edge_url}?hours={hours}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch status: {response.status}")

                data = await response.json()

                # Parse metrics from response
                metrics_dict = {m["label"]: m["value"] for m in data.get("metrics", [])}

                return GuardianMetrics(
                    timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    window_hours=data.get("window_hours", hours),
                    vault_nodes=metrics_dict.get("VaultNodes", 0),
                    ache_events=metrics_dict.get("AcheEvents(lookback)", 0),
                    scarindex_avg=metrics_dict.get("ScarIndex(avg)"),
                    scarindex_latest=metrics_dict.get("ScarIndex(latest)"),
                    alerts_24h=metrics_dict.get("Alerts(24h)", 0),
                    scar_status=data.get("scar_status", "❔"),
                    scar_score=data.get("scar_score"),
                    coherence_components=data.get("coherence_components"),
                    pid_state=data.get("pid_state"),
                    panic_frames=data.get("panic_frames", 0),
                )

    async def post_witness_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send witness protocol events to Spiral API."""

        if not self.api_url:
            raise ValueError("GUARDIAN_API_URL is required for witness protocol")

        url = f"{self.api_url.rstrip('/')}/witness/event"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status >= 400:
                    detail = await response.text()
                    raise Exception(f"Witness event failed: {response.status} {detail}")
                return await response.json()

    async def fetch_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """Fetch witness claim status via API proxy."""

        if not self.api_url:
            raise ValueError("GUARDIAN_API_URL is required for witness protocol")

        url = f"{self.api_url.rstrip('/')}/witness/claim/{claim_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    raise Exception("Claim not found")
                if response.status >= 400:
                    detail = await response.text()
                    raise Exception(f"Claim lookup failed: {response.status} {detail}")
                return await response.json()

    def create_status_embed(self, metrics: GuardianMetrics) -> discord.Embed:
        """Create a rich embed for Guardian status."""
        # Determine color based on status
        color_map = {
            "🟢": discord.Color.green(),
            "🟠": discord.Color.orange(),
            "🔴": discord.Color.red(),
        }
        color = color_map.get(metrics.scar_status, discord.Color.greyple())

        # Determine status text
        status_text = {
            "🟢": "COHERENT",
            "🟠": "WARNING",
            "🔴": "CRITICAL",
        }.get(metrics.scar_status, "UNKNOWN")

        # Create embed
        embed = discord.Embed(
            title="🛡️ SpiralOS Guardian Heartbeat",
            description=f"**Status:** {metrics.scar_status} {status_text}",
            color=color,
            timestamp=datetime.fromisoformat(metrics.timestamp.replace("Z", "+00:00")),
        )

        # Add ScarIndex field
        scar_display = f"{metrics.scar_score:.3f}" if metrics.scar_score else "N/A"
        embed.add_field(
            name="📊 ScarIndex",
            value=f"**Current:** {scar_display}\n**Target:** 0.70\n**Window:** {metrics.window_hours}h",
            inline=True,
        )

        # Add system metrics
        embed.add_field(
            name="🔢 System Metrics",
            value=(
                f"**VaultNodes:** {metrics.vault_nodes}\n"
                f"**Ache Events:** {metrics.ache_events}\n"
                f"**Alerts (24h):** {metrics.alerts_24h}"
            ),
            inline=True,
        )

        # Add coherence breakdown if available
        if metrics.coherence_components:
            comp = metrics.coherence_components
            coherence_text = (
                f"**Narrative:** {comp.get('narrative', 0):.2f} (30%)\n"
                f"**Social:** {comp.get('social', 0):.2f} (25%)\n"
                f"**Economic:** {comp.get('economic', 0):.2f} (25%)\n"
                f"**Technical:** {comp.get('technical', 0):.2f} (20%)"
            )
            embed.add_field(name="🌀 Coherence Components", value=coherence_text, inline=False)

        # Add PID controller state if available
        if metrics.pid_state:
            pid = metrics.pid_state
            pid_text = (
                f"**Error:** {pid.get('error', 0):+.3f}\n" f"**Guidance Scale:** {pid.get('guidance_scale', 1.0):.2f}"
            )
            embed.add_field(name="⚙️ PID Controller", value=pid_text, inline=True)

        # Add panic frame warning if active
        if metrics.panic_frames and metrics.panic_frames > 0:
            embed.add_field(
                name="🚨 PANIC FRAMES ACTIVE",
                value=f"**{metrics.panic_frames}** active panic frame(s)\nSystem operations may be frozen",
                inline=False,
            )

        # Add out-of-band warning
        if metrics.scar_score and (metrics.scar_score < 0.6 or metrics.scar_score >= 1.4):
            embed.add_field(name="⚠️ Coherence Alert", value="ScarIndex out of healthy band (0.6–1.4)", inline=False)

        # Add footer
        embed.set_footer(
            text="Where coherence becomes currency 🜂",
            icon_url="https://raw.githubusercontent.com/ZoaGrad/mythotech-spiralos/main/assets/spiral_icon.png",
        )

        return embed

    def create_panic_embed(self, metrics: GuardianMetrics) -> discord.Embed:
        """Create a critical alert embed for Panic Frame activation."""
        embed = discord.Embed(
            title="🚨 PANIC FRAME ACTIVATED (F4)",
            description="**Status:** 🔴 CRITICAL\n**System operations halted pending recovery**",
            color=discord.Color.dark_red(),
            timestamp=datetime.fromisoformat(metrics.timestamp.replace("Z", "+00:00")),
        )

        scar_display = f"{metrics.scar_score:.3f}" if metrics.scar_score else "N/A"
        embed.add_field(
            name="📉 ScarIndex",
            value=f"**Current:** {scar_display}\n**Threshold:** 0.30\n**Status:** Below minimum",
            inline=False,
        )

        if metrics.coherence_components:
            comp = metrics.coherence_components
            coherence_text = ""
            for name, value in comp.items():
                emoji = "🔴" if value < 0.3 else "⚠️" if value < 0.5 else "🟢"
                coherence_text += f"**{name.title()}:** {value:.2f} {emoji}\n"

            embed.add_field(name="📉 Coherence Breakdown", value=coherence_text, inline=False)

        embed.add_field(
            name="🔧 Recommended Actions",
            value=(
                "1. Review recent Ache events\n"
                "2. Check Oracle Council status\n"
                "3. Verify VaultNode integrity\n"
                "4. Await recovery protocol completion"
            ),
            inline=False,
        )

        embed.set_footer(text="@Guardians - Immediate attention required")

        return embed

    @tasks.loop(hours=6)
    async def heartbeat_task(self):
        """Periodic heartbeat task (every 6 hours)."""
        try:
            if not self.channel_id:
                return

            channel = self.get_channel(self.channel_id)
            if not channel:
                print(f"❌ Channel {self.channel_id} not found")
                return

            metrics = await self.fetch_guardian_status(hours=24)

            # Check for panic frame
            if metrics.scar_score and metrics.scar_score < 0.30:
                embed = self.create_panic_embed(metrics)
            else:
                embed = self.create_status_embed(metrics)

            await channel.send(embed=embed)
            print(f"✅ Heartbeat sent to channel {self.channel_id}")

        except Exception as e:
            print(f"❌ Heartbeat task error: {e}")

    @heartbeat_task.before_loop
    async def before_heartbeat(self):
        """Wait until bot is ready before starting heartbeat."""
        await self.wait_until_ready()


# Create bot instance
bot = GuardianBot()


# Slash Commands
@bot.tree.command(name="claim", description="Submit a STREAM witness claim")
@app_commands.describe(target_id="Target user id", payload="JSON payload for the claim")
async def claim_command(interaction: discord.Interaction, target_id: str, payload: str):
    """Submit a witness claim via Supabase edge proxy."""

    await interaction.response.defer(ephemeral=True)

    try:
        event = {
            "initiator_id": str(interaction.user.id),
            "target_id": target_id,
            "payload": payload,
        }
        data = await bot.post_witness_event(event)
        await interaction.followup.send(
            f"✅ Claim submitted. ID: `{data.get('claim_id')}`", ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Claim submission failed: {e}", ephemeral=True)


@bot.tree.command(name="witness", description="Submit a witness assessment")
@app_commands.describe(
    claim_id="Claim identifier",
    semantic="Semantic resonance score",
    emotional="Emotional resonance score",
    contextual="Contextual resonance score",
    notes="Optional notes",
)
async def witness_command(
    interaction: discord.Interaction,
    claim_id: str,
    semantic: float,
    emotional: float,
    contextual: float,
    notes: Optional[str] = None,
):
    """Submit an assessment for a STREAM witness claim."""

    await interaction.response.defer(ephemeral=True)

    try:
        assessment = {
            "claim_id": claim_id,
            "witness_id": str(interaction.user.id),
            "semantic": semantic,
            "emotional": emotional,
            "contextual": contextual,
            "notes": notes,
        }
        data = await bot.post_witness_event(assessment)
        finalized = data.get("finalized")
        status_line = "" if not finalized else f" → auto-finalized: {finalized}"
        await interaction.followup.send(
            f"✅ Assessment recorded for `{claim_id}`{status_line}", ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Witness submission failed: {e}", ephemeral=True)


@bot.tree.command(name="status", description="Get current Guardian system status or witness claim")
@app_commands.describe(hours="Time window in hours (default: 24)", claim_id="Optional witness claim id")
async def status_command(interaction: discord.Interaction, hours: int = 24, claim_id: Optional[str] = None):
    """Get current system status or witness claim state."""
    await interaction.response.defer(ephemeral=bool(claim_id))

    try:
        if claim_id:
            claim = await bot.fetch_claim_status(claim_id)
            await interaction.followup.send(
                f"📜 Claim **{claim_id}** → {claim.get('status', 'unknown').upper()} (ρΣ={claim.get('rho_sigma')})",
                ephemeral=True,
            )
            return

        metrics = await bot.fetch_guardian_status(hours=hours)
        embed = bot.create_status_embed(metrics)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching status: {e}", ephemeral=True)


@bot.tree.command(name="scarindex", description="Get detailed ScarIndex breakdown")
async def scarindex_command(interaction: discord.Interaction):
    """Get detailed ScarIndex information."""
    await interaction.response.defer()

    try:
        metrics = await bot.fetch_guardian_status(hours=24)

        embed = discord.Embed(
            title="📊 ScarIndex Detailed Analysis",
            description="Coherence measurement across four dimensions",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )

        if metrics.scar_score:
            embed.add_field(name="Current ScarIndex", value=f"**{metrics.scar_score:.3f}**", inline=False)

        if metrics.coherence_components:
            comp = metrics.coherence_components

            # Calculate weighted contributions
            narrative_contrib = comp.get("narrative", 0) * 0.30
            social_contrib = comp.get("social", 0) * 0.25
            economic_contrib = comp.get("economic", 0) * 0.25
            technical_contrib = comp.get("technical", 0) * 0.20

            embed.add_field(
                name="🌀 Component Breakdown",
                value=(
                    f"**Narrative (30%):** {comp.get('narrative', 0):.3f} → {narrative_contrib:.3f}\n"
                    f"**Social (25%):** {comp.get('social', 0):.3f} → {social_contrib:.3f}\n"
                    f"**Economic (25%):** {comp.get('economic', 0):.3f} → {economic_contrib:.3f}\n"
                    f"**Technical (20%):** {comp.get('technical', 0):.3f} → {technical_contrib:.3f}"
                ),
                inline=False,
            )

        if metrics.pid_state:
            pid = metrics.pid_state
            embed.add_field(
                name="⚙️ PID Controller State",
                value=(
                    f"**Target:** {pid.get('target', 0.70):.2f}\n"
                    f"**Error:** {pid.get('error', 0):+.3f}\n"
                    f"**Integral:** {pid.get('integral', 0):+.3f}\n"
                    f"**Derivative:** {pid.get('derivative', 0):+.3f}\n"
                    f"**Guidance Scale:** {pid.get('guidance_scale', 1.0):.3f}"
                ),
                inline=False,
            )

        embed.add_field(
            name="📏 Thresholds",
            value=(
                "**≥ 0.70:** Healthy (target setpoint)\n"
                "**< 0.67:** Under PID review\n"
                "**< 0.30:** 🚨 Panic Frame (F4 circuit breaker)"
            ),
            inline=False,
        )

        embed.set_footer(text="ScarIndex = Σ(weights × components) × PID_guidance_scale")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching ScarIndex: {e}", ephemeral=True)


@bot.tree.command(name="panic", description="Check for active Panic Frames")
async def panic_command(interaction: discord.Interaction):
    """Check for active Panic Frames."""
    await interaction.response.defer()

    try:
        metrics = await bot.fetch_guardian_status(hours=24)

        if metrics.panic_frames and metrics.panic_frames > 0:
            embed = bot.create_panic_embed(metrics)
        else:
            embed = discord.Embed(
                title="✅ No Active Panic Frames",
                description="System coherence is within acceptable parameters",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc),
            )

            if metrics.scar_score:
                embed.add_field(
                    name="Current ScarIndex", value=f"**{metrics.scar_score:.3f}** (Threshold: 0.30)", inline=False
                )

            embed.add_field(
                name="ℹ️ About Panic Frames",
                value=(
                    "Panic Frames (F4 Circuit Breaker) activate when ScarIndex drops below 0.30. "
                    "This freezes all operations until coherence is restored through the recovery protocol."
                ),
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Error checking panic status: {e}", ephemeral=True)


@bot.tree.command(name="metrics", description="Get system metrics for custom time window")
@app_commands.describe(hours="Time window in hours (1-168)")
async def metrics_command(interaction: discord.Interaction, hours: int):
    """Get metrics for custom time window."""
    await interaction.response.defer()

    if hours < 1 or hours > 168:
        await interaction.followup.send("❌ Hours must be between 1 and 168 (1 week)", ephemeral=True)
        return

    try:
        metrics = await bot.fetch_guardian_status(hours=hours)

        embed = discord.Embed(
            title=f"📈 System Metrics ({hours}h window)",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📊 Activity",
            value=(
                f"**VaultNodes (total):** {metrics.vault_nodes}\n"
                f"**Ache Events:** {metrics.ache_events}\n"
                f"**Alerts:** {metrics.alerts_24h}"
            ),
            inline=True,
        )

        embed.add_field(
            name="🌀 Coherence",
            value=(
                f"**ScarIndex (avg):** {metrics.scarindex_avg:.3f if metrics.scarindex_avg else 'N/A'}\n"
                f"**ScarIndex (latest):** {metrics.scarindex_latest:.3f if metrics.scarindex_latest else 'N/A'}\n"
                f"**Status:** {metrics.scar_status}"
            ),
            inline=True,
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching metrics: {e}", ephemeral=True)


@bot.tree.command(name="vault", description="Get recent VaultNode information")
async def vault_command(interaction: discord.Interaction):
    """Get recent VaultNode seals."""
    await interaction.response.defer()

    try:
        metrics = await bot.fetch_guardian_status(hours=24)

        embed = discord.Embed(
            title="🔐 VaultNode Status",
            description="Immutable audit trail with Merkle-linked accountability",
            color=discord.Color.purple(),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(name="📊 Statistics", value=f"**Total VaultNodes:** {metrics.vault_nodes}", inline=False)

        embed.add_field(
            name="ℹ️ About VaultNodes",
            value=(
                "VaultNodes provide immutable accountability for all governance actions. "
                "Each node is Merkle-linked with ΔΩ version lineage, ensuring complete auditability."
            ),
            inline=False,
        )

        embed.set_footer(text="All governance actions are sealed and immutable")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching vault info: {e}", ephemeral=True)


def main():
    """Main entry point."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN environment variable is required")
        sys.exit(1)

    try:
        bot.run(token)
    except KeyboardInterrupt:
        print("\n👋 Guardian Bot shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
