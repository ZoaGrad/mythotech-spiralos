// types/constitutional-milestone.ts
// ΔΩ.142.1 — Constitutional Portal Artifact Schema
// Compatible with tRPC + React Query + Supabase

import { z } from "zod";

/**
 * Strongly-typed interface for constitutional milestone artifacts.
 * Mirrors the JSON schema stored in Supabase (`constitutional_milestones.metadata`).
 */
export interface ConstitutionalMilestone {
  milestone: string;                // e.g., "ΔΩ.142.1"
  title: string;                    // Document title
  label: string;                    // Short UI label
  phase: string;                    // Phase name (e.g., "Ratification Support")
  category: string;                 // "Research Document", "Governance Record", etc.
  status: "pending" | "active" | "verified" | "archived";
  repository: string;               // GitHub repo URL
  url: string;                      // Direct artifact link
  linked_nodes: string[];           // Related VaultNodes
  authors: string[];                // Contributor list
  version: string;                  // Version tag (ΔΩ.x.x)
  last_updated: string;             // ISO timestamp
  license: string;                  // e.g., "CC-BY-SA-4.0"
  visuals?: {
    diagram?: string;               // "mermaid", "image", etc.
    theme?: string;                 // "scarindex-dark"
    icon?: string;                  // e.g., "📜"
  };
  integration?: {
    supabase_table?: string;        // default: "constitutional_milestones"
    dashboard_component?: string;   // e.g., "ResearchArtifacts"
    live_feed?: boolean;            // real-time updates toggle
  };
  description?: string;             // Full narrative summary
}

/**
 * Zod schema for runtime validation.
 * Use with tRPC router or React Query data fetch to ensure integrity.
 */
export const ConstitutionalMilestoneSchema = z.object({
  milestone: z.string(),
  title: z.string(),
  label: z.string(),
  phase: z.string(),
  category: z.string(),
  status: z.enum(["pending", "active", "verified", "archived"]),
  repository: z.string().url(),
  url: z.string().url(),
  linked_nodes: z.array(z.string()),
  authors: z.array(z.string()),
  version: z.string(),
  last_updated: z.string(),
  license: z.string(),
  visuals: z
    .object({
      diagram: z.string().optional(),
      theme: z.string().optional(),
      icon: z.string().optional(),
    })
    .optional(),
  integration: z
    .object({
      supabase_table: z.string().optional(),
      dashboard_component: z.string().optional(),
      live_feed: z.boolean().optional(),
    })
    .optional(),
  description: z.string().optional(),
});

export type ConstitutionalMilestoneType = z.infer<typeof ConstitutionalMilestoneSchema>;