"use client";

import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface CausalLink {
    id: string;
    created_at: string;
    created_by: string | null;
    cause_type: string;
    weight: number;
    notes: any;
    phase_lock_hash: string | null;
    temporal_anchor_id: string | null;

    source_event_id: string;
    source_created_at: string;
    source_event_type: string;
    source_component: string;
    source_payload: any;

    target_event_id: string;
    target_created_at: string;
    target_event_type: string;
    target_component: string;
    target_payload: any;
}

export function useCausalityMesh() {
    const [links, setLinks] = useState<CausalLink[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchLinks = async () => {
            const { data, error } = await supabase
                .from("view_causal_links")
                .select("*");

            if (error) {
                console.error("Failed to fetch causal links", error);
                setError(error.message);
                setLoading(false);
                return;
            }

            setLinks((data || []) as CausalLink[]);
            setLoading(false);
        };

        fetchLinks();
        const interval = setInterval(fetchLinks, 5000); // poll every 5s

        return () => clearInterval(interval);
    }, []);

    return { links, loading, error };
}
