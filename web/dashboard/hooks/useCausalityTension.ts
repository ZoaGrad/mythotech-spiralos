"use client";

import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface CausalityTensionNode {
  event_id: string;
  latest_event_at: string;
  event_type: string;
  component: string;
  total_weight_norm: number;
  mesh_tension_max: number;
  severity_dominant: string | null;
}

export function useCausalityTension() {
  const [nodes, setNodes] = useState<CausalityTensionNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNodes = async () => {
      const { data, error } = await supabase
        .from("view_causality_tension")
        .select("*");

      if (error) {
        console.error("Failed to fetch causality tension", error);
        setError(error.message);
        setLoading(false);
        return;
      }

      setNodes((data || []) as CausalityTensionNode[]);
      setLoading(false);
    };

    fetchNodes();
    const interval = setInterval(fetchNodes, 5000);
    return () => clearInterval(interval);
  }, []);

  return { nodes, loading, error };
}
