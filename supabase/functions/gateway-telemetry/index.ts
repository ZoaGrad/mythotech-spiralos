// ============================================================================
// Gateway Telemetry Edge Function
// ============================================================================
// Purpose: Process webhook transmissions from Ω-Δ-Φ workflow gateway
// Constitutional Alignment: Validate sovereignty constraints before storage
// C₅-C₇ Tensor Analysis: Extract real-time metrics for coherence monitoring
// ============================================================================

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// ============================================================================
// CORS Configuration
// ============================================================================
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// ============================================================================
// Type Definitions
// ============================================================================

interface GatewayTransmission {
  bridge_id: string;
  resonance_score: number;
  necessity_score: number;
  payload?: Record<string, unknown>;
  constraint_tensor?: Record<string, unknown>;
}

interface SovereigntyConstraints {
  min_resonance: number;
  min_necessity: number;
  min_sovereignty_index: number;
}

interface C5C7TensorMetrics {
  coherence_c5: number;
  coherence_c6: number;
  coherence_c7: number;
  tensor_magnitude: number;
  sovereignty_index: number;
}

// ============================================================================
// Sovereignty Constraint Validation
// ============================================================================

function validateSovereigntyConstraints(
  transmission: GatewayTransmission,
  constraints: SovereigntyConstraints = {
    min_resonance: 0.0,
    min_necessity: 0.0,
    min_sovereignty_index: 0.0,
  }
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Validate resonance_score bounds [0, 1]
  if (transmission.resonance_score < 0 || transmission.resonance_score > 1) {
    errors.push(`resonance_score must be between 0 and 1 (got ${transmission.resonance_score})`);
  }

  // Validate necessity_score bounds [0, 1]
  if (transmission.necessity_score < 0 || transmission.necessity_score > 1) {
    errors.push(`necessity_score must be between 0 and 1 (got ${transmission.necessity_score})`);
  }

  // Validate bridge_id is present
  if (!transmission.bridge_id || transmission.bridge_id.trim().length === 0) {
    errors.push('bridge_id is required and cannot be empty');
  }

  // Calculate sovereignty index
  const sovereignty_index = (transmission.resonance_score + transmission.necessity_score) / 2.0;

  // Validate against minimum thresholds
  if (transmission.resonance_score < constraints.min_resonance) {
    errors.push(
      `resonance_score ${transmission.resonance_score} below threshold ${constraints.min_resonance}`
    );
  }

  if (transmission.necessity_score < constraints.min_necessity) {
    errors.push(
      `necessity_score ${transmission.necessity_score} below threshold ${constraints.min_necessity}`
    );
  }

  if (sovereignty_index < constraints.min_sovereignty_index) {
    errors.push(
      `sovereignty_index ${sovereignty_index} below threshold ${constraints.min_sovereignty_index}`
    );
  }

  // Validate JSONB fields are objects
  if (transmission.payload && typeof transmission.payload !== 'object') {
    errors.push('payload must be a valid JSON object');
  }

  if (transmission.constraint_tensor && typeof transmission.constraint_tensor !== 'object') {
    errors.push('constraint_tensor must be a valid JSON object');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

// ============================================================================
// C₅-C₇ Tensor Metrics Extraction
// ============================================================================

function extractC5C7TensorMetrics(transmission: GatewayTransmission): C5C7TensorMetrics {
  const { resonance_score, necessity_score, constraint_tensor } = transmission;

  // Calculate sovereignty index
  const sovereignty_index = (resonance_score + necessity_score) / 2.0;

  // Extract tensor components from constraint_tensor JSONB
  // C₅ = Narrative Coherence (from tensor or derived from resonance)
  const coherence_c5 = (constraint_tensor?.c5 as number) ?? resonance_score * 0.8;

  // C₆ = Social Coherence (from tensor or derived from necessity)
  const coherence_c6 = (constraint_tensor?.c6 as number) ?? necessity_score * 0.7;

  // C₇ = Economic Coherence (from tensor or interpolated)
  const coherence_c7 = (constraint_tensor?.c7 as number) ?? sovereignty_index * 0.6;

  // Calculate tensor magnitude (Euclidean norm)
  const tensor_magnitude = Math.sqrt(
    Math.pow(coherence_c5, 2) + Math.pow(coherence_c6, 2) + Math.pow(coherence_c7, 2)
  );

  return {
    coherence_c5,
    coherence_c6,
    coherence_c7,
    tensor_magnitude,
    sovereignty_index,
  };
}

// ============================================================================
// Main Handler
// ============================================================================

serve(async (req) => {
  // Handle OPTIONS for CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') || '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
    );

    // Parse incoming transmission
    const transmission: GatewayTransmission = await req.json();

    // Extract sovereignty constraints from query params or use defaults
    const url = new URL(req.url);
    const constraints: SovereigntyConstraints = {
      min_resonance: parseFloat(url.searchParams.get('min_resonance') || '0.0'),
      min_necessity: parseFloat(url.searchParams.get('min_necessity') || '0.0'),
      min_sovereignty_index: parseFloat(url.searchParams.get('min_sovereignty_index') || '0.0'),
    };

    // Validate sovereignty constraints
    const validation = validateSovereigntyConstraints(transmission, constraints);

    if (!validation.valid) {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'Sovereignty constraint validation failed',
          details: validation.errors,
        }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 400,
        }
      );
    }

    // Extract C₅-C₇ tensor metrics
    const tensorMetrics = extractC5C7TensorMetrics(transmission);

    // Enrich payload with tensor metrics
    const enrichedPayload = {
      ...(transmission.payload || {}),
      tensor_metrics: tensorMetrics,
      validated_at: new Date().toISOString(),
    };

    // Insert transmission into database
    const { error, data } = await supabase
      .from('gateway_transmissions')
      .insert([
        {
          bridge_id: transmission.bridge_id,
          resonance_score: transmission.resonance_score,
          necessity_score: transmission.necessity_score,
          payload: enrichedPayload,
          constraint_tensor: transmission.constraint_tensor || {},
        },
      ])
      .select();

    if (error) {
      // Handle unique constraint violations gracefully
      if (error.code === '23505') {
        return new Response(
          JSON.stringify({
            success: false,
            error: 'Duplicate bridge_id - transmission already recorded',
            bridge_id: transmission.bridge_id,
          }),
          {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 409,
          }
        );
      }
      throw error;
    }

    // Return success with enriched data
    return new Response(
      JSON.stringify({
        success: true,
        data: data?.[0],
        tensor_metrics: tensorMetrics,
        message: 'Gateway transmission recorded successfully',
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 201,
      }
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';

    console.error('Gateway telemetry error:', message);

    return new Response(
      JSON.stringify({
        success: false,
        error: 'Internal server error processing gateway transmission',
        details: message,
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    );
  }
});

// ============================================================================
// Edge Function Deployed
// ============================================================================
// VaultNode Seal: ΔΩ.147.0 - Gateway Telemetry Processing
// Constitutional Compliance: ✓ Sovereignty constraints validated
// Tensor Analysis: ✓ C₅-C₇ metrics extracted and enriched
// ============================================================================
