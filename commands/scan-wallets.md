---
name: scan-wallets
description: Scan a directory recursively for potential Bitcoin wallet files
arguments:
  - name: directory
    description: Directory path to scan for wallet.dat files
    required: true
---

# Scan Directory for Bitcoin Wallets

Recursively scan a directory to find potential Bitcoin wallet.dat files.

## Execution

```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 recovery_wizard.py --scandir "$directory" --dry-run
```

This performs a dry run that:
1. Recursively scans all subdirectories
2. Identifies .dat files larger than 10KB
3. Analyzes each for Bitcoin wallet signatures
4. Reports findings without extracting keys

## What It Detects

The scanner looks for:
- Berkeley DB file headers (versions 4.x, 5.x, 6.x)
- Bitcoin-specific patterns: `defaultkey`, `bestblock`, `pool`, `key`, `wkey`, `ckey`, `mkey`
- Returns confidence scores (0-100%) for each file

## Output

Lists found wallet candidates with:
- File path
- File size
- Confidence score
- Detection details

Files with 40%+ confidence are flagged as likely Bitcoin wallets.

## Next Steps

After scanning, use `/recover-wallet` to fully process discovered wallets.
