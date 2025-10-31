# SpiralOS Deployment Guide

This guide provides step-by-step instructions for deploying SpiralOS in production.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 22.04+ recommended) or macOS
- **Python**: 3.9 or higher
- **PostgreSQL**: 15 or higher (via Supabase)
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 1GB free space

### External Services

1. **Supabase Account**
   - Sign up at https://supabase.com
   - Create a new project
   - Note your project ID and API keys

2. **OpenAI API Access**
   - Sign up at https://platform.openai.com
   - Generate an API key
   - Ensure you have access to required models:
     - gpt-4.1-mini
     - gpt-4.1-nano
     - gemini-2.5-flash (via OpenAI-compatible endpoint)

3. **GitHub Repository** (optional, for VaultNode audit trail)
   - Create a repository for audit logs
   - Generate a personal access token with repo permissions

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/ZoaGrad/emotion-sdk-tuner-.git
cd emotion-sdk-tuner-/spiralos
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Supabase Configuration
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# GitHub Configuration (optional)
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO=owner/repo-name

# SpiralOS Configuration
SPIRALOS_TARGET_SCARINDEX=0.7
SPIRALOS_ENABLE_CONSENSUS=true
SPIRALOS_ENABLE_PANIC_FRAMES=true

# PID Controller Configuration
PID_KP=1.0
PID_KI=0.5
PID_KD=0.2
```

### 4. Set Up Supabase Database

#### Option A: Using Supabase MCP (Recommended)

```bash
# Ensure Supabase MCP is configured
manus-mcp-cli tool call execute_sql --server supabase \
  --input "{\"project_id\":\"YOUR_PROJECT_ID\",\"query\":\"$(cat schema.sql)\"}"
```

#### Option B: Using Supabase Dashboard

1. Log in to your Supabase dashboard
2. Navigate to SQL Editor
3. Copy the contents of `schema.sql`
4. Execute the SQL script

#### Option C: Using Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref YOUR_PROJECT_ID

# Apply migrations
supabase db push
```

### 5. Verify Database Setup

```python
python3 << 'EOF'
from supabase_integration import SupabaseClient
import asyncio

async def verify():
    client = SupabaseClient()
    status = await client.get_current_coherence_status()
    print(f"Database connection successful!")
    print(f"Current coherence: {status}")

asyncio.run(verify())
EOF
```

### 6. Run Tests

```bash
# Run the test suite
python3 test_spiralos.py

# Expected output: 5-6 tests passing
```

### 7. Start SpiralOS

```python
python3 << 'EOF'
from spiralos import SpiralOS
import asyncio

async def main():
    # Initialize SpiralOS
    spiralos = SpiralOS(
        target_scarindex=0.7,
        enable_consensus=True,
        enable_panic_frames=True
    )
    
    print("SpiralOS initialized successfully!")
    print(f"Law: {spiralos.get_law_of_recursive_alignment()}")
    
    # Get system status
    status = spiralos.get_system_status()
    print(f"System Status: {status['system']['status']}")
    print(f"Coherence: {status['coherence']['current_scarindex']:.4f}")

asyncio.run(main())
EOF
```

## Production Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY schema.sql ./

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python3", "spiralos.py"]
```

Build and run:

```bash
# Build Docker image
docker build -t spiralos:latest .

# Run container
docker run -d \
  --name spiralos \
  --env-file .env \
  -p 8000:8000 \
  spiralos:latest
```

### Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spiralos
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spiralos
  template:
    metadata:
      labels:
        app: spiralos
    spec:
      containers:
      - name: spiralos
        image: spiralos:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: spiralos-secrets
              key: openai-api-key
        - name: SUPABASE_PROJECT_ID
          valueFrom:
            configMapKeyRef:
              name: spiralos-config
              key: supabase-project-id
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

## Monitoring and Observability

### Health Checks

Create a health check endpoint:

```python
from fastapi import FastAPI
from spiralos import SpiralOS

app = FastAPI()
spiralos = SpiralOS()

@app.get("/health")
async def health_check():
    status = spiralos.get_system_status()
    return {
        "status": "healthy" if status['system']['status'] == 'OPERATIONAL' else "unhealthy",
        "scarindex": status['coherence']['current_scarindex'],
        "panic_frames": status['panic_frames']['active_count']
    }

@app.get("/metrics")
async def metrics():
    return spiralos.get_system_status()
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spiralos.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('spiralos')
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge, Histogram

# Metrics
transmutations_total = Counter('spiralos_transmutations_total', 'Total transmutations')
scarindex_current = Gauge('spiralos_scarindex_current', 'Current ScarIndex value')
panic_frames_active = Gauge('spiralos_panic_frames_active', 'Active panic frames')
transmutation_duration = Histogram('spiralos_transmutation_duration_seconds', 'Transmutation duration')
```

## Backup and Recovery

### Database Backups

```bash
# Using Supabase CLI
supabase db dump -f backup.sql

# Restore from backup
supabase db reset
psql -h db.your-project.supabase.co -U postgres -f backup.sql
```

### VaultNode Audit Trail

The VaultNode system automatically creates an immutable audit trail in GitHub. To verify:

```bash
# Clone audit trail repository
git clone https://github.com/YOUR_ORG/audit-trail.git

# Verify chain integrity
python3 << 'EOF'
from supabase_integration import SpiralOSBackend
import asyncio

async def verify_chain():
    backend = SpiralOSBackend()
    # Verification logic here
    print("Audit trail verified")

asyncio.run(verify_chain())
EOF
```

## Performance Tuning

### PID Controller Tuning

Use the Ziegler-Nichols method for optimal tuning:

```python
from ache_pid_controller import AchePIDController

controller = AchePIDController()

# Auto-tune using Ziegler-Nichols
ultimate_gain = 2.0  # Determined from oscillation test
ultimate_period = 10.0  # Determined from oscillation test

params = controller.auto_tune_ziegler_nichols(ultimate_gain, ultimate_period)

print(f"Tuned parameters:")
print(f"  Kp: {params.kp:.4f}")
print(f"  Ki: {params.ki:.4f}")
print(f"  Kd: {params.kd:.4f}")
```

### Database Optimization

```sql
-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_scarindex_timestamp 
  ON scarindex_calculations(created_at DESC, scarindex);

CREATE INDEX CONCURRENTLY idx_panic_frames_status_timestamp 
  ON panic_frames(status, created_at DESC);

-- Analyze tables for query optimization
ANALYZE scarindex_calculations;
ANALYZE panic_frames;
ANALYZE verification_records;
```

### Consensus Protocol Optimization

```python
# Adjust consensus parameters for performance
from coherence_protocol import DistributedCoherenceProtocol

protocol = DistributedCoherenceProtocol(
    consensus_threshold=2,  # Require 2-of-3 consensus
    total_providers=3       # Query 3 providers
)

# For faster response (lower accuracy):
protocol_fast = DistributedCoherenceProtocol(
    consensus_threshold=1,  # Accept single provider
    total_providers=1
)
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failures

```bash
# Check Supabase status
curl https://YOUR_PROJECT_ID.supabase.co/rest/v1/

# Verify credentials
echo $SUPABASE_PROJECT_ID
echo $SUPABASE_ANON_KEY
```

#### 2. OpenAI API Errors

```python
# Test API connection
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": "test"}]
)
print("API connection successful!")
```

#### 3. Panic Frame Not Resolving

```python
# Manually resolve panic frame
from panic_frames import PanicFrameManager

manager = PanicFrameManager()
success = manager.resolve_panic_frame(
    panic_frame_id="YOUR_FRAME_ID",
    final_scarindex=0.5  # Above threshold
)
print(f"Resolution successful: {success}")
```

## Security Considerations

### API Key Management

- Never commit API keys to version control
- Use environment variables or secret management services
- Rotate keys regularly
- Use different keys for development and production

### Database Security

```sql
-- Enable Row Level Security
ALTER TABLE scarindex_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE panic_frames ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read their own data"
  ON scarindex_calculations FOR SELECT
  USING (auth.uid() = user_id);
```

### Network Security

- Use HTTPS for all API communications
- Enable Supabase SSL connections
- Implement rate limiting
- Use VPN for database access in production

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple SpiralOS instances behind a load balancer
- Use Redis for distributed state management
- Implement message queues for async processing

### Vertical Scaling

- Increase database connection pool size
- Allocate more memory for PID controller history
- Use faster storage for VaultNode commits

## Maintenance

### Regular Tasks

1. **Daily**
   - Monitor ScarIndex trends
   - Check for active Panic Frames
   - Review system logs

2. **Weekly**
   - Analyze PID controller performance
   - Review consensus verification rates
   - Check database performance

3. **Monthly**
   - Update dependencies
   - Review and tune PID parameters
   - Audit VaultNode chain integrity
   - Backup database

### Upgrade Procedure

```bash
# 1. Backup current state
supabase db dump -f backup-$(date +%Y%m%d).sql

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Run migrations (if any)
# Apply new schema changes

# 5. Run tests
python3 test_spiralos.py

# 6. Restart services
docker-compose restart spiralos
```

## Support and Resources

- **Documentation**: See README.md and TECHNICAL_SPEC.md
- **GitHub Issues**: https://github.com/ZoaGrad/emotion-sdk-tuner-/issues
- **Supabase Docs**: https://supabase.com/docs
- **OpenAI API Docs**: https://platform.openai.com/docs

---

**Last Updated**: 2025-10-30  
**Version**: 1.0.0
