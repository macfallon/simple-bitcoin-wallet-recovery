#!/bin/bash
# Test script for Simple Bitcoin Wallet Recovery

echo "🧪 Testing Simple Bitcoin Wallet Recovery Tool"
echo "============================================="
echo

# Test 1: Check if wallet.dat from Downloads is detected
echo "Test 1: Detecting known Bitcoin wallet"
python3 lib/wallet_detector.py "/mnt/c/users/josh/Downloads/wallet.dat"
echo

# Test 2: Check a non-wallet file
echo "Test 2: Detecting non-wallet file"
python3 lib/wallet_detector.py "README.md"
echo

# Test 3: Test balance checker with known address
echo "Test 3: Checking balance of genesis block address"
python3 -c "from lib.balance_checker import check_balance; print(check_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'))"
echo

echo "✅ Tests complete!"
echo
echo "To run full recovery on your wallet:"
echo "python3 recovery_wizard.py /path/to/wallet.dat"