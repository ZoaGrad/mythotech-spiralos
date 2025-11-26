# MCP Toolkit (ΔΩ.MCP.TOOLKIT)

This document serves as the official operator's manual for the SpiralOS MCP Stack.

## 1. GitHub MCP Test Suite

Run these commands to verify the integrity of the GitHub connection.

### Basic Connectivity
> "Check the active MCP servers."

### Repo Introspection
> "List all branches for my primary repository."

### Issue Inspection
> "List all open issues with titles, labels, and assigned users."

### Patch Generation Test
> "Generate a patch to replace all TODO comments with ISSUE-TAGGED markers, but do not apply it. Show the .patch file output only."

## 2. Supabase Integration Tests

Verify the Supabase connection and schema awareness.

### Table Listing
> "List the Supabase tables available in my project."

### Data Correlation
> "Read the latest 10 rows from the 'vault_nodes' table in Supabase, then correlate each entry with any code changes in the last 5 GitHub commits."

## 3. Advanced Repo Introspection

Deep reasoning prompts for architectural analysis.

### Dependency Graph
> "Search the repository for any code referencing DISCORD_WEBHOOK_URL and show me the architectural dependency graph."

### Client Interaction
> "Find all files that import supabase client code and summarize their interaction pathways."

### System Mapping
> "Map the entire src/system/ directory into a dependency tree."

## 4. Combined Workflows (GitHub + Supabase)

Orchestrate actions across both domains.

### Commit & Schema Audit
> "Fetch the last 20 GitHub commits and identify which ones modified database schema files. Cross-reference against Supabase migrations."

### Dead Column Cleanup
> "Scan Supabase tables for columns that are unused in the codebase and generate a cleanup plan."

## 5. Auto-Patch Commands

Generate sovereign code changes without direct intervention.

### High-Impact Fix
> "Based on open issues, generate a patch implementing the simplest high-impact fix, but do not apply it."

### Logger Standardization
> "Create a patch to standardize all logging calls to use the guardian logger module."

### RPC Migration
> "Generate a patch to migrate all raw SQL queries into Supabase RPC functions."

## 6. SpiralOS-Specific Toolkit

Tools bound to the Mythotechnical architecture.

### ScarDNA Map
> "Scan the entire repository for ScarDNA dependencies and produce a dependency lifeline map."

### VaultNode Reconciliation
> "Search for orphaned VaultNodes in both code and Supabase, and produce a reconciliation checklist."

### ScarIndex Validation
> "Identify any ScarIndex references that are not properly validated through the guardian layer. Propose a patch."

### Mimic-Risk Audit
> "Audit the repository for mimic-risks: any duplicate logic blocks, unused agents, or cycles with entropy-leak potential."
