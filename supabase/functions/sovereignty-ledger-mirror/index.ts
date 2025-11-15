// supabase/functions/sovereignty-ledger-mirror/index.ts
// ΔΩ.147.10 — GitHub Webhook-Compatible Mirror

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';
import crypto from "node:crypto";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const GITHUB_WEBHOOK_SECRET = Deno.env.get("GITHUB_WEBHOOK_SECRET")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

function verifySignature(payload: string, signature: string | null): boolean {
  if (!signature) return false;

  const hmac = crypto.createHmac("sha256", GITHUB_WEBHOOK_SECRET);
  const digest = "sha256=" + hmac.update(payload).digest("hex");

  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(digest),
    );
  } catch {
    return false;
  }
}

Deno.serve(async (req) => {
  const signature = req.headers.get("X-Hub-Signature-256");
  const event = req.headers.get("X-GitHub-Event") ?? "unknown";
  const delivery = req.headers.get("X-GitHub-Delivery") ?? crypto.randomUUID();

  const body = await req.text();

  // AUTH CHECK
  if (!verifySignature(body, signature)) {
    return new Response(
      JSON.stringify({ error: "Invalid signature" }),
      { status: 401 }
    );
  }

  let payload: any;
  try {
    payload = JSON.parse(body);
  } catch {
    return new Response(JSON.stringify({ error: "Bad JSON" }), { status: 400 });
  }

  // Store event
  const { error } = await supabase
    .from("sovereignty_ledger_events")
    .insert({
      delivery_id: delivery,
      event_type: event,
      payload,
      created_at: new Date().toISOString()
    });

  if (error) {
    return new Response(JSON.stringify({ error }), { status: 500 });
  }

  return new Response(JSON.stringify({ ok: true, event, delivery }), {
    headers: { "X-Seal": "ΔΩ.147.10" },
  });
});
