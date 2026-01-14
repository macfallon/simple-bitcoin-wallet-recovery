---
name: Bitcoin Wallet Recovery
description: Use this skill when the user mentions wallet.dat files, Bitcoin recovery, old Bitcoin wallets, recovering cryptocurrency, or checking Bitcoin balances. Activates for discussions about extracting private keys from old wallets.
version: 2.0.0
---

# Bitcoin Wallet Recovery Skill

This skill provides knowledge for recovering Bitcoin from old wallet.dat files.

## When to Use

Activate when the user:
- Mentions `wallet.dat` files
- Asks about recovering Bitcoin from old wallets
- Has .dat files they want to check for Bitcoin
- Needs to extract private keys from Bitcoin Core wallets
- Wants to check if an old file is a Bitcoin wallet
- Needs help transferring recovered Bitcoin to a modern wallet

## Available Commands

| Command | Purpose |
|---------|---------|
| `/recover-wallet <path>` | Full recovery wizard - scan, detect, extract, check balances |
| `/scan-wallets <directory>` | Scan directory for potential wallet files |
| `/detect-wallet <file>` | Check if a file is a Bitcoin wallet |
| `/check-balance <address>` | Check balance of a Bitcoin address |

## Recovery Process Overview

1. **Detection**: Identify Bitcoin wallet.dat files using Berkeley DB header analysis
2. **Extraction**: Use pywallet to extract private keys from the wallet
3. **Balance Check**: Query multiple blockchain APIs to find addresses with funds
4. **Export**: Save private keys in formats compatible with modern wallets (Electrum, Bitcoin Core, etc.)
5. **Transfer**: Guide user to import keys and transfer Bitcoin to secure storage

## Key Technical Details

### Wallet.dat Structure
- Berkeley DB format (versions 4.x, 5.x, 6.x supported)
- Contains: private keys, public keys, addresses, transaction history
- May be encrypted (requires password)

### Address Formats Supported
- Legacy P2PKH (starts with `1`)
- P2SH (starts with `3`)
- Native SegWit bech32 (starts with `bc1`)

### Balance APIs Used
- blockchain.info (batch queries, 100 addresses at once)
- blockstream.info (verification)
- blockcypher.com (backup)
- mempool.space (real-time mempool)

## Security Guidance

When helping users with wallet recovery:

1. **Never expose private keys** in conversation logs or shared documents
2. **Recommend immediate transfer** - don't leave Bitcoin in recovered wallets
3. **Secure deletion** - remind users to securely delete exported key files
4. **Test transactions** - suggest sending small amount first to verify
5. **Hardware wallets** - recommend transferring to hardware wallet for long-term storage

## Common Issues

### Berkeley DB Not Found
```bash
# Ubuntu/Debian
sudo apt-get install python3-bsddb3 libdb-dev

# macOS
brew install berkeley-db
pip install bsddb3
```

### Encrypted Wallets
If wallet is encrypted, pywallet will prompt for password. Without the correct password, keys cannot be extracted.

### Empty Wallets
Many old wallets have 0 balance because:
- Bitcoin was already spent
- Wallet was from testnet
- It's a backup from before any Bitcoin was received

## Example Workflow

```
User: "I found an old wallet.dat file on my backup drive"

1. First, detect if it's actually a Bitcoin wallet:
   /detect-wallet /path/to/wallet.dat

2. If detected as wallet, run full recovery:
   /recover-wallet /path/to/wallet.dat

3. Check the output directory for results:
   - summary_report.txt shows overview
   - funded_wallets/ contains any Bitcoin found

4. If Bitcoin found, guide user through transfer to secure wallet
```

## File Locations

Plugin scripts are located at `${CLAUDE_PLUGIN_ROOT}`:
- `recovery_wizard.py` - Main orchestrator
- `pywallet.py` - Key extraction (modified fork)
- `lib/wallet_detector.py` - Wallet detection
- `lib/balance_checker.py` - Balance verification
- `lib/secure_exporter.py` - Key export formats
