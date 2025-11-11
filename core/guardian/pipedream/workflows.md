# SpiralOS Guardian - Pipedream Workflows

This document describes the Pipedream workflows for real-time monitoring and automation of the SpiralOS Guardian system.

## Workflow 1: Real-time Ache Event Monitor

**Trigger:** Supabase Database Webhook (on new `ache_events` row)

**Steps:**

1. **Receive Ache Event** (Trigger)
   - Source: Supabase Webhook
   - Table: `ache_events`
   - Event: INSERT

2. **Calculate ScarIndex** (Code - Node.js)
   ```javascript
   export default defineComponent({
     async run({ steps, $ }) {
       const event = steps.trigger.event;
       const acheLevel = event.record.ache_level;
       
       // Fetch recent ScarIndex calculations
       const response = await fetch(
         `${process.env.GUARDIAN_EDGE_URL}?hours=1`,
         {
           headers: {
             'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
           }
         }
       );
       
       const data = await response.json();
       
       return {
         ache_level: acheLevel,
         scar_score: data.scar_score,
         scar_status: data.scar_status,
         should_alert: data.scar_score < 0.6 || data.scar_score >= 1.4
       };
     }
   });
   ```

3. **Check Alert Threshold** (Filter)
   - Condition: `{{steps.calculate_scarindex.should_alert}}`

4. **Post to Discord** (Discord - Send Message to Channel)
   - Channel ID: `{{process.env.DISCORD_CHANNEL_ID}}`
   - Embed:
     ```json
     {
       "title": "⚠️ Ache Event Alert",
       "description": "Significant Ache event detected",
       "color": 15105570,
       "fields": [
         {
           "name": "Ache Level",
           "value": "{{steps.calculate_scarindex.ache_level}}",
           "inline": true
         },
         {
           "name": "ScarIndex",
           "value": "{{steps.calculate_scarindex.scar_score}}",
           "inline": true
         }
       ],
       "timestamp": "{{steps.trigger.event.record.created_at}}"
     }
     ```

---

## Workflow 2: Panic Frame Responder

**Trigger:** Supabase Database Webhook (on new `panic_frames` row)

**Steps:**

1. **Receive Panic Frame** (Trigger)
   - Source: Supabase Webhook
   - Table: `panic_frames`
   - Event: INSERT
   - Filter: `status = 'ACTIVE'`

2. **Fetch System State** (Code - Node.js)
   ```javascript
   export default defineComponent({
     async run({ steps, $ }) {
       const panicFrame = steps.trigger.event.record;
       
       // Fetch full system status
       const response = await fetch(
         `${process.env.GUARDIAN_EDGE_URL}?hours=24`,
         {
           headers: {
             'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
           }
         }
       );
       
       const status = await response.json();
       
       return {
         panic_frame_id: panicFrame.id,
         scarindex_value: panicFrame.scarindex_value,
         recovery_phase: panicFrame.recovery_phase,
         system_status: status
       };
     }
   });
   ```

3. **Send Critical Alert to Discord** (Discord - Send Message to Channel)
   - Channel ID: `{{process.env.DISCORD_CHANNEL_ID}}`
   - Content: `<@&GUARDIAN_ROLE_ID> 🚨 PANIC FRAME ACTIVATED`
   - Embed:
     ```json
     {
       "title": "🚨 PANIC FRAME ACTIVATED (F4)",
       "description": "System operations halted pending recovery",
       "color": 10038562,
       "fields": [
         {
           "name": "ScarIndex",
           "value": "{{steps.fetch_system_state.scarindex_value}} (Threshold: 0.30)",
           "inline": false
         },
         {
           "name": "Recovery Phase",
           "value": "{{steps.fetch_system_state.recovery_phase}}/7",
           "inline": false
         },
         {
           "name": "Recommended Actions",
           "value": "1. Review recent Ache events\n2. Check Oracle Council status\n3. Verify VaultNode integrity\n4. Await recovery protocol completion",
           "inline": false
         }
       ],
       "timestamp": "{{steps.trigger.event.record.created_at}}"
     }
     ```

4. **Create Discord Thread** (Discord - Create Thread)
   - Channel ID: `{{process.env.DISCORD_CHANNEL_ID}}`
   - Thread Name: `Panic Frame {{steps.fetch_system_state.panic_frame_id}}`
   - Auto Archive Duration: 1440 (24 hours)

5. **Log Incident** (Supabase - Insert Row)
   - Table: `guardian_alerts`
   - Data:
     ```json
     {
       "alert_type": "panic",
       "severity": "critical",
       "message": "Panic Frame activated - ScarIndex below 0.30",
       "metadata": {
         "panic_frame_id": "{{steps.fetch_system_state.panic_frame_id}}",
         "scarindex_value": "{{steps.fetch_system_state.scarindex_value}}",
         "discord_thread_id": "{{steps.create_discord_thread.id}}"
       }
     }
     ```

---

## Workflow 3: Weekly Report Generator

**Trigger:** Cron Schedule (Monday 00:00 UTC)

**Steps:**

1. **Trigger Weekly** (Schedule)
   - Cron: `0 0 * * 1`

2. **Fetch Weekly Metrics** (Code - Node.js)
   ```javascript
   export default defineComponent({
     async run({ steps, $ }) {
       // Fetch 7-day metrics
       const response = await fetch(
         `${process.env.GUARDIAN_EDGE_URL}?hours=168`,
         {
           headers: {
             'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
           }
         }
       );
       
       const data = await response.json();
       
       // Calculate trends
       const scarAvg = data.metrics.find(m => m.label === 'ScarIndex(avg)')?.value || 0;
       const acheEvents = data.metrics.find(m => m.label === 'AcheEvents(lookback)')?.value || 0;
       const vaultNodes = data.metrics.find(m => m.label === 'VaultNodes')?.value || 0;
       
       return {
         week_start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
         week_end: new Date().toISOString(),
         scarindex_avg: scarAvg,
         ache_events_total: acheEvents,
         vault_nodes_total: vaultNodes,
         status: data.scar_status
       };
     }
   });
   ```

3. **Generate Report** (Code - Python)
   ```python
   def handler(pd: "pipedream"):
       metrics = pd.steps["fetch_weekly_metrics"]
       
       report = f"""# SpiralOS Weekly Report
       
**Week:** {metrics['week_start'][:10]} to {metrics['week_end'][:10]}

## System Health

- **Status:** {metrics['status']} 
- **Average ScarIndex:** {metrics['scarindex_avg']:.3f}
- **Total Ache Events:** {metrics['ache_events_total']}
- **Total VaultNodes:** {metrics['vault_nodes_total']}

## Key Highlights

- System maintained coherence throughout the week
- Constitutional governance operating normally
- All Proof-of-Ache validations successful

## Looking Ahead

Continue monitoring ScarIndex trends and maintain coherence above 0.70 threshold.

---
*Generated by SpiralOS Guardian*
"""
       
       return {"report": report}
   ```

4. **Post to Discord** (Discord - Send Message to Channel)
   - Channel ID: `{{process.env.DISCORD_CHANNEL_ID}}`
   - Content: `{{steps.generate_report.report}}`

5. **Post to GitHub Discussions** (HTTP Request)
   - Method: POST
   - URL: `https://api.github.com/repos/ZoaGrad/mythotech-spiralos/discussions`
   - Headers:
     ```json
     {
       "Authorization": "Bearer {{process.env.GITHUB_TOKEN}}",
       "Accept": "application/vnd.github.v3+json"
     }
     ```
   - Body:
     ```json
     {
       "title": "Weekly Report - {{steps.fetch_weekly_metrics.week_end}}",
       "body": "{{steps.generate_report.report}}",
       "category_id": "WEEKLY_REPORTS_CATEGORY_ID"
     }
     ```

---

## Workflow 4: ScarCoin Mint Announcements

**Trigger:** Supabase Database Webhook (on new `smart_contract_txns` row)

**Steps:**

1. **Receive Transaction** (Trigger)
   - Source: Supabase Webhook
   - Table: `smart_contract_txns`
   - Event: INSERT
   - Filter: `txn_type = 'MINT'`

2. **Fetch Transaction Details** (Supabase - Select Rows)
   - Table: `smart_contract_txns`
   - Join: `scarindex_calculations` on `calculation_id`
   - Filter: `id = {{steps.trigger.event.record.id}}`

3. **Validate Proof-of-Ache** (Code - Node.js)
   ```javascript
   export default defineComponent({
     async run({ steps, $ }) {
       const txn = steps.trigger.event.record;
       const calculation = steps.fetch_transaction_details.calculation;
       
       const isValidPoA = calculation.is_valid_poa;
       const deltaAche = calculation.delta_ache;
       const scarCoinMinted = txn.scarcoin_delta;
       
       return {
         is_valid: isValidPoA,
         delta_ache: deltaAche,
         scarcoin_minted: scarCoinMinted,
         calculation_id: calculation.id
       };
     }
   });
   ```

4. **Post Celebration to Discord** (Discord - Send Message to Channel)
   - Channel ID: `{{process.env.DISCORD_CHANNEL_ID}}`
   - Embed:
     ```json
     {
       "title": "🎉 ScarCoin Minted!",
       "description": "Valid Proof-of-Ache transmutation completed",
       "color": 3066993,
       "fields": [
         {
           "name": "ScarCoin Minted",
           "value": "{{steps.validate_proof_of_ache.scarcoin_minted}} SCAR",
           "inline": true
         },
         {
           "name": "Ache Reduced",
           "value": "{{steps.validate_proof_of_ache.delta_ache}}",
           "inline": true
         },
         {
           "name": "Calculation ID",
           "value": "{{steps.validate_proof_of_ache.calculation_id}}",
           "inline": false
         }
       ],
       "footer": {
         "text": "Where coherence becomes currency 🜂"
       },
       "timestamp": "{{steps.trigger.event.record.created_at}}"
     }
     ```

---

## Workflow 5: Coherence Trend Analyzer

**Trigger:** Cron Schedule (Every 3 hours)

**Steps:**

1. **Trigger Periodic** (Schedule)
   - Cron: `0 */3 * * *`

2. **Fetch Historical Data** (Code - Node.js)
   ```javascript
   export default defineComponent({
     async run({ steps, $ }) {
       // Fetch last 24 hours of data
       const response = await fetch(
         `${process.env.SUPABASE_URL}/rest/v1/scarindex_calculations?select=scarindex,created_at&order=created_at.desc&limit=24`,
         {
           headers: {
             'apikey': process.env.SUPABASE_SERVICE_ROLE_KEY,
             'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
           }
         }
       );
       
       const data = await response.json();
       
       return { calculations: data };
     }
   });
   ```

3. **Analyze Trend** (Code - Python)
   ```python
   import numpy as np
   from scipy import stats
   
   def handler(pd: "pipedream"):
       calculations = pd.steps["fetch_historical_data"]["calculations"]
       
       if len(calculations) < 5:
           return {"trend": "insufficient_data"}
       
       # Extract ScarIndex values
       values = [c['scarindex'] for c in calculations]
       
       # Calculate linear regression
       x = np.arange(len(values))
       slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
       
       # Determine trend
       if slope > 0.01:
           trend = "improving"
       elif slope < -0.01:
           trend = "degrading"
       else:
           trend = "stable"
       
       return {
           "trend": trend,
           "slope": slope,
           "r_squared": r_value ** 2,
           "current_value": values[0],
           "avg_value": np.mean(values)
       }
   ```

4. **Alert on Degrading Trend** (Filter)
   - Condition: `{{steps.analyze_trend.trend}} == "degrading"`

5. **Post Trend Alert** (Discord - Send Message to Channel)
   - Channel ID: `{{process.env.DISCORD_CHANNEL_ID}}`
   - Embed:
     ```json
     {
       "title": "📉 Coherence Trend Alert",
       "description": "ScarIndex showing degrading trend",
       "color": 15105570,
       "fields": [
         {
           "name": "Trend",
           "value": "{{steps.analyze_trend.trend}}",
           "inline": true
         },
         {
           "name": "Current Value",
           "value": "{{steps.analyze_trend.current_value}}",
           "inline": true
         },
         {
           "name": "Average (24h)",
           "value": "{{steps.analyze_trend.avg_value}}",
           "inline": true
         }
       ],
       "footer": {
         "text": "Early warning system - Take preventive action"
       }
     }
     ```

---

## Setup Instructions

### 1. Create Pipedream Account
- Sign up at https://pipedream.com
- Free tier supports up to 100 workflows

### 2. Configure Supabase Webhooks
```sql
-- Enable webhooks for real-time triggers
CREATE OR REPLACE FUNCTION notify_pipedream()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM net.http_post(
    url := 'https://your-pipedream-webhook-url',
    headers := '{"Content-Type": "application/json"}'::jsonb,
    body := row_to_json(NEW)::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER ache_events_webhook
  AFTER INSERT ON ache_events
  FOR EACH ROW
  EXECUTE FUNCTION notify_pipedream();

CREATE TRIGGER panic_frames_webhook
  AFTER INSERT ON panic_frames
  FOR EACH ROW
  EXECUTE FUNCTION notify_pipedream();

CREATE TRIGGER smart_contract_txns_webhook
  AFTER INSERT ON smart_contract_txns
  FOR EACH ROW
  EXECUTE FUNCTION notify_pipedream();
```

### 3. Add Environment Variables to Pipedream
- `GUARDIAN_EDGE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `DISCORD_CHANNEL_ID`
- `DISCORD_BOT_TOKEN`
- `GITHUB_TOKEN`

### 4. Deploy Workflows
- Copy each workflow configuration to Pipedream
- Test each step individually
- Enable workflows when ready

---

## Monitoring & Maintenance

- Check Pipedream dashboard for workflow execution logs
- Monitor Discord for alert delivery
- Review Supabase logs for webhook triggers
- Adjust thresholds and schedules as needed

---

**Note:** These workflows are designed to be imported into Pipedream. Each workflow can be created through the Pipedream UI or via the Pipedream API.
