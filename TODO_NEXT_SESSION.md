# TODO for Next Session - Sample Wallet Analysis

## Immediate Priority: Analyze Sample Wallet Privacy

Before making the sample wallet public, we MUST:

### 1. Create Wallet History Analyzer

```python
# wallet_history_analyzer.py
# This script needs to:
- Load all addresses from wallet
- Query blockchain for full transaction history
- Calculate maximum balance ever held
- Show balance over time
- Identify privacy risks
```

### 2. Key Questions to Answer

1. **What was the maximum balance?**
   - If it held significant funds, more privacy risk

2. **When was it last used?**
   - Recent activity = higher risk

3. **Are addresses clustered?**
   - Do transactions link addresses together?

4. **Any identifiable patterns?**
   - Regular transactions?
   - Links to known services?

### 3. Sample Wallet Decision Tree

```
IF wallet.max_balance > 1 BTC:
    → Create fresh test wallet
ELIF wallet.last_activity < 2 years ago:
    → Create fresh test wallet  
ELIF wallet.has_identifiable_patterns:
    → Create fresh test wallet
ELSE:
    → Safe to use (with warnings)
```

### 4. Creating a Fresh Test Wallet (if needed)

```bash
# Option A: Create with minimal history
1. Generate new wallet
2. Add 0.00001 BTC to 2-3 addresses
3. Wait for confirmations
4. Empty it
5. Use as safe example

# Option B: Use testnet
1. Create testnet wallet
2. Add testnet coins (free)
3. Perfect for demos, zero risk
```

### 5. Scripts to Create Next

1. **wallet_history_analyzer.py**
   ```python
   - analyze_wallet_history(addresses)
   - get_max_balance(addresses)
   - plot_balance_over_time(addresses)
   - assess_privacy_risk(addresses)
   ```

2. **create_test_wallet.py**
   ```python
   - generate_test_wallet()
   - add_test_transactions()
   - export_for_demo()
   ```

### 6. Quick Commands to Run

```bash
# Check what's in our sample wallet
python3 pywallet.py --wallet=tests/sample_wallet.dat --dumpwallet > sample_analysis.json

# Count addresses
cat sample_analysis.json | jq '.keys | length'

# Get all addresses
cat sample_analysis.json | jq -r '.keys[].addr' > sample_addresses.txt

# Quick balance check
python3 check_balances.py  # (modify to use sample_addresses.txt)
```

### 7. GitHub Publication Steps (after wallet decision)

```bash
# When ready to publish
git init
git add .
git commit -m "Initial commit: Simple Bitcoin Wallet Recovery Tool

Success story: Recovered 0.12145281 BTC (~$13,062) from an old wallet.dat file.
This tool streamlines the process for others to check their old drives."

# Create repo on GitHub web interface first
git remote add origin https://github.com/[username]/simple-bitcoin-wallet-recovery.git
git push -u origin main
```

### 8. Key Context for AI Assistant

**IMPORTANT**: When you resume, the first task is to analyze the sample wallet's blockchain history before making any part of this project public. The sample wallet at `tests/sample_wallet.dat` needs privacy analysis.

**Success Story**: We recovered 0.12145281 BTC from a wallet with 1,008 addresses, 5 of which had funds.

**Main Feature**: `python3 recovery_wizard.py --scandir /path` creates organized results in a timestamped directory.

**Architecture**: 
- Wizard orchestrates the process
- Detector identifies wallets
- Checker verifies balances
- Exporter creates secure outputs