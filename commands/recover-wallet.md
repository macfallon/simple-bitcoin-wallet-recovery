---
name: recover-wallet
description: Recover Bitcoin from wallet.dat files - the main recovery wizard
arguments:
  - name: path
    description: Path to a wallet.dat file or directory to scan for wallets
    required: true
  - name: dry-run
    description: Preview what would be scanned without actually processing (optional)
    required: false
---

# Bitcoin Wallet Recovery Command

Run the full Bitcoin wallet recovery wizard on the specified path.

## Prerequisites

Before running, ensure Python dependencies are installed:
```bash
cd ${CLAUDE_PLUGIN_ROOT}
pip install -r requirements.txt
```

On Ubuntu/Debian, also install Berkeley DB:
```bash
sudo apt-get install python3-bsddb3 libdb-dev
```

## Execution

Run the recovery wizard with the provided path:

```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 recovery_wizard.py "$ARGUMENTS"
```

If `--dry-run` is specified, add that flag:
```bash
python3 recovery_wizard.py --scandir "$path" --dry-run
```

For a single wallet file:
```bash
python3 recovery_wizard.py "$path"
```

For a directory scan:
```bash
python3 recovery_wizard.py --scandir "$path"
```

## What This Does

1. **Scans** the specified path for .dat files (if directory) or analyzes a single file
2. **Detects** which files are valid Bitcoin wallet.dat files using Berkeley DB header analysis
3. **Extracts** private keys from detected wallets using pywallet
4. **Checks balances** across multiple blockchain APIs (blockchain.info, blockstream, blockcypher, mempool.space)
5. **Exports** funded wallet keys in multiple formats for import into modern wallets

## Output

Results are saved to a timestamped directory:
- `bitcoin_recovery_YYYYMMDD_HHMMSS/output/summary_report.txt` - Overview
- `bitcoin_recovery_YYYYMMDD_HHMMSS/output/funded_wallets/` - Wallets with Bitcoin found
- `bitcoin_recovery_YYYYMMDD_HHMMSS/output/empty_wallets/` - Wallets with no balance

## Security Notes

- Private keys are written to files with restricted permissions (600 on Unix)
- Always transfer Bitcoin to a secure wallet immediately after recovery
- Securely delete exported private key files after successful transfer
- Never share private keys or upload them to cloud storage
