# Sprint 1: Data Ingestion Engine

**Antifragile SRE Platform MVP - Product Direction 1**

This is the raw data ingestion pipeline that connects to the Datadog API (read-only) to fetch historical metric data and stores it in a Supabase (PostgreSQL) database.

## Architecture

- **Source**: Datadog API (read-only access)
- **Metrics**: `system.cpu.idle` and `system.load.1` (last 1 hour, averaged by host)
- **Storage**: Supabase (PostgreSQL)
- **Language**: Python 3.x
- **Libraries**: `datadog-api-client`, `supabase-py`

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your actual credentials:

- **DATADOG_API_KEY**: Your Datadog API key (read-only recommended)
- **DATADOG_APP_KEY**: Your Datadog application key
- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_KEY**: Your Supabase service role key or anon key with insert permissions

### 3. Create the Database Table

Run the SQL schema in your Supabase SQL Editor:

```bash
# Copy the contents of create_metrics_table.sql
# Paste into Supabase SQL Editor at:
# https://supabase.com/dashboard/project/_/sql
```

Or use the Supabase CLI:

```bash
supabase db execute -f create_metrics_table.sql
```

## Usage

Run the data ingestion script:

```bash
python datadog_ingestion.py
```

The script will:

1. Connect to Datadog API using your credentials
2. Fetch `system.cpu.idle` and `system.load.1` metrics for the last 1 hour
3. Aggregate metrics by host
4. Store all data points in the Supabase `metrics` table

## Output Example

```
Fetching metrics from 2025-12-12T10:00:00 to 2025-12-12T11:00:00
Fetching metric: system.cpu.idle
  Retrieved 60 data points
Fetching metric: system.load.1
  Retrieved 60 data points
Successfully inserted 120 metric data points.

Total metrics ingested: 120
```

## Database Schema

The `metrics` table structure:

| Column       | Type              | Description                                    |
|--------------|-------------------|------------------------------------------------|
| id           | BIGSERIAL         | Primary key (auto-increment)                   |
| host         | VARCHAR(255)      | Hostname from Datadog                          |
| metric_name  | VARCHAR(255)      | Metric name (e.g., system.cpu.idle)            |
| value        | DOUBLE PRECISION  | Metric value (averaged by host)                |
| timestamp    | TIMESTAMPTZ       | Timestamp of the metric data point             |
| created_at   | TIMESTAMPTZ       | When the record was inserted (auto-generated)  |

Indexes are created on `host`, `metric_name`, `timestamp`, and a composite index for efficient querying.

## Security Notes

- **API Keys**: Never commit your `.env` file to version control
- **Read-Only Access**: Use read-only Datadog API keys when possible
- **Supabase Keys**: Use service role key for backend operations, never expose in client-side code

## Next Steps

This is Sprint 1 only. Future sprints will add:

- **Sprint 2**: ScarOperator for anomaly detection
- **Sprint 3**: Real-time alerting and visualization
- **Sprint 4**: Multi-cloud support and advanced analytics

## Troubleshooting

**No metrics retrieved:**
- Verify your Datadog API credentials are correct
- Check that your Datadog account has data for the specified metrics
- Ensure the time range contains data (last 1 hour)

**Database insertion fails:**
- Verify your Supabase credentials are correct
- Ensure the `metrics` table has been created
- Check that your Supabase key has INSERT permissions

**Import errors:**
- Run `pip install -r requirements.txt` to install all dependencies
- Ensure you're using Python 3.9 or newer
