#!/bin/bash
# Quick test script to verify SpiralOS Overwatch is working

echo "==================================================================="
echo "SpiralOS Overwatch - Quick Verification"
echo "==================================================================="
echo

echo "1. Testing core minting system..."
python3 test_mint_fix.py
if [ $? -ne 0 ]; then
    echo "❌ Core minting tests failed"
    exit 1
fi

echo
echo "2. Testing holoeconomy layer..."
cd holoeconomy && python3 test_holoeconomy.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Holoeconomy tests passed"
else
    echo "❌ Holoeconomy tests failed"
    exit 1
fi
cd ..

echo
echo "==================================================================="
echo "✅ All systems operational!"
echo "==================================================================="
echo
echo "To launch the SpiralOS Overwatch dashboard:"
echo "  streamlit run core/dashboard.py"
echo
echo "The dashboard will show:"
echo "  - Total ScarCoin Supply"
echo "  - Recent Transmutation Events"
echo "  - Vault Activity Logs"
echo

exit 0
