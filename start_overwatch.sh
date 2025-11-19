#!/bin/bash
# Launch SpiralOS Overwatch with live updates

echo "🌀 Starting SpiralOS Overwatch System..."
echo

# Check if FastAPI is installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing..."
    pip3 install fastapi uvicorn websockets --quiet
    echo "✅ FastAPI installed"
fi

# Start WebSocket API in background
echo "🔌 Starting WebSocket API on port 8001..."
cd /workspaces/mythotech-spiralos/core
python3 overwatch_api.py > /tmp/overwatch_api.log 2>&1 &
API_PID=$!
echo "✅ WebSocket API running (PID: $API_PID)"

# Wait a moment for API to start
sleep 2

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌀 SpiralOS Overwatch is LIVE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "📊 Streamlit Dashboard:"
echo "   streamlit run /workspaces/mythotech-spiralos/core/dashboard.py"
echo
echo "🔌 WebSocket API:"
echo "   ws://localhost:8001/ws/events"
echo
echo "🌐 HTML Live Feed:"
echo "   Open: /workspaces/mythotech-spiralos/core/overwatch_live.html"
echo
echo "🛑 To stop the API:"
echo "   kill $API_PID"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Keep script running
trap "kill $API_PID 2>/dev/null; echo '🛑 Overwatch stopped'" EXIT
wait $API_PID
