// Sovereignty Metrics Dashboard - Main Logic
// VaultNode Seal: ΔΩ.147.3

// Supabase Configuration
const SUPABASE_URL = 'https://xlmrnjatawslawquwzpf.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsbXJuamF0YXdzbGF3cXV3enBmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA5MzA3MTAsImV4cCI6MjA0NjUwNjcxMH0.xoKGIdE7sL5AkGJjhJdLNfQ7JLBKgOD6P5HGFj7JjQU';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Global state
let transmissionsData = [];
let refreshInterval = null;

// Initialize dashboard
async function initDashboard() {
    console.log('🔮 Initializing Sovereignty Metrics Dashboard...');
    updateStatus('loading', 'Loading data...');
    
    await fetchTransmissions();
    renderAllCharts();
    updateMetricCards();
    
    // Set up auto-refresh every 30 seconds
    refreshInterval = setInterval(async () => {
        console.log('🔄 Auto-refreshing data...');
        await fetchTransmissions();
        renderAllCharts();
        updateMetricCards();
    }, 30000);
    
    updateStatus('active', 'Live');
}

// Fetch transmissions from Supabase
async function fetchTransmissions() {
    try {
        const { data, error } = await supabase
            .from('gateway_transmissions')
            .select('bridge_id, resonance_score, necessity_score, created_at, payload')
            .order('created_at', { ascending: false })
            .limit(100);
        
        if (error) {
            console.error('❌ Supabase fetch error:', error);
            updateStatus('error', 'API Error');
            return;
        }
        
        transmissionsData = data || [];
        console.log(`✅ Fetched ${transmissionsData.length} transmissions`);
        
        // Update last updated timestamp
        const now = new Date();
        document.getElementById('lastUpdate').textContent = 
            `Last updated: ${now.toLocaleTimeString()}`;
            
    } catch (err) {
        console.error('❌ Fetch error:', err);
        updateStatus('error', 'Connection Failed');
    }
}

// Calculate sovereignty index
function calculateSovereigntyIndex(resonance, necessity) {
    return (resonance + necessity) / 2.0;
}

// Update metric overview cards
function updateMetricCards() {
    if (transmissionsData.length === 0) {
        document.getElementById('avgSovereignty').textContent = '0.00';
        document.getElementById('highCount').textContent = '0';
        document.getElementById('lowCount').textContent = '0';
        return;
    }
    
    // Calculate average sovereignty
    const avgSovereignty = transmissionsData.reduce((sum, t) => {
        return sum + calculateSovereigntyIndex(t.resonance_score, t.necessity_score);
    }, 0) / transmissionsData.length;
    
    // Count high and low sovereignty transmissions
    const highCount = transmissionsData.filter(t => {
        const index = calculateSovereigntyIndex(t.resonance_score, t.necessity_score);
        return index >= 0.75;
    }).length;
    
    const lowCount = transmissionsData.filter(t => {
        const index = calculateSovereigntyIndex(t.resonance_score, t.necessity_score);
        return index < 0.6;
    }).length;
    
    // Update DOM
    document.getElementById('avgSovereignty').textContent = avgSovereignty.toFixed(3);
    document.getElementById('highCount').textContent = highCount;
    document.getElementById('lowCount').textContent = lowCount;
    
    // Update sovereignty trend indicator
    const trendEl = document.getElementById('sovereigntyTrend');
    if (avgSovereignty >= 0.75) {
        trendEl.textContent = '🟢 High';
        trendEl.className = 'metric-trend high';
    } else if (avgSovereignty >= 0.6) {
        trendEl.textContent = '🟡 Medium';
        trendEl.className = 'metric-trend medium';
    } else {
        trendEl.textContent = '🔴 Low';
        trendEl.className = 'metric-trend low';
    }
}

// Update status indicator
function updateStatus(status, text) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

// Render all charts
function renderAllCharts() {
    renderTrendChart();
    renderDistributionChart();
    renderHeartbeatChart();
}

// Render 24-hour trend chart
function renderTrendChart() {
    const now = new Date();
    const last24h = new Date(now - 24 * 60 * 60 * 1000);
    
    const chartData = transmissionsData
        .filter(t => new Date(t.created_at) >= last24h)
        .reverse()
        .map(t => ({
            time: new Date(t.created_at).toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            }),
            resonance: t.resonance_score,
            necessity: t.necessity_score,
            sovereignty: calculateSovereigntyIndex(t.resonance_score, t.necessity_score)
        }));
    
    if (chartData.length === 0) {
        document.getElementById('trendChart').innerHTML = 
            '<div class="no-data">No data in last 24 hours</div>';
        return;
    }
    
    // Simple text representation (since Recharts requires React)
    const chartHtml = `
        <div class="simple-chart">
            ${chartData.map(d => `
                <div class="chart-row">
                    <span class="chart-label">${d.time}</span>
                    <div class="chart-bars">
                        <div class="bar resonance" style="width: ${d.resonance * 100}%" 
                             title="Resonance: ${d.resonance.toFixed(3)}"></div>
                        <div class="bar necessity" style="width: ${d.necessity * 100}%" 
                             title="Necessity: ${d.necessity.toFixed(3)}"></div>
                        <div class="bar sovereignty" style="width: ${d.sovereignty * 100}%" 
                             title="Sovereignty: ${d.sovereignty.toFixed(3)}"></div>
                    </div>
                    <span class="chart-value">${d.sovereignty.toFixed(3)}</span>
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('trendChart').innerHTML = chartHtml;
}

// Render distribution chart
function renderDistributionChart() {
    const distribution = {
        high: 0,
        medium: 0,
        low: 0
    };
    
    transmissionsData.forEach(t => {
        const index = calculateSovereigntyIndex(t.resonance_score, t.necessity_score);
        if (index >= 0.75) distribution.high++;
        else if (index >= 0.6) distribution.medium++;
        else distribution.low++;
    });
    
    const total = transmissionsData.length || 1;
    
    const chartHtml = `
        <div class="distribution-chart">
            <div class="dist-bar">
                <div class="dist-segment high" style="width: ${(distribution.high / total) * 100}%">
                    <span>${distribution.high}</span>
                </div>
                <div class="dist-segment medium" style="width: ${(distribution.medium / total) * 100}%">
                    <span>${distribution.medium}</span>
                </div>
                <div class="dist-segment low" style="width: ${(distribution.low / total) * 100}%">
                    <span>${distribution.low}</span>
                </div>
            </div>
            <div class="dist-legend">
                <div class="legend-item"><span class="legend-color high"></span> High (≥0.75)</div>
                <div class="legend-item"><span class="legend-color medium"></span> Medium (0.6-0.75)</div>
                <div class="legend-item"><span class="legend-color low"></span> Low (<0.6)</div>
            </div>
        </div>
    `;
    
    document.getElementById('distributionChart').innerHTML = chartHtml;
}

// Render Guardian heartbeat timeline
function renderHeartbeatChart() {
    const guardianHeartbeats = transmissionsData
        .filter(t => t.bridge_id && t.bridge_id.startsWith('guardian-heartbeat'))
        .slice(0, 20)
        .reverse();
    
    if (guardianHeartbeats.length === 0) {
        document.getElementById('heartbeatChart').innerHTML = 
            '<div class="no-data">No Guardian heartbeats detected</div>';
        return;
    }
    
    const chartHtml = `
        <div class="heartbeat-timeline">
            ${guardianHeartbeats.map(h => {
                const sovereignty = calculateSovereigntyIndex(h.resonance_score, h.necessity_score);
                const statusClass = sovereignty >= 0.75 ? 'high' : sovereignty >= 0.6 ? 'medium' : 'low';
                const time = new Date(h.created_at).toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                return `
                    <div class="heartbeat-item ${statusClass}">
                        <div class="heartbeat-dot"></div>
                        <div class="heartbeat-info">
                            <div class="heartbeat-time">${time}</div>
                            <div class="heartbeat-scores">
                                R: ${h.resonance_score.toFixed(3)} | 
                                N: ${h.necessity_score.toFixed(3)} | 
                                S: ${sovereignty.toFixed(3)}
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    document.getElementById('heartbeatChart').innerHTML = chartHtml;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initDashboard);
