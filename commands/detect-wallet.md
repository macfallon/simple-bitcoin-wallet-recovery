---
name: detect-wallet
description: Analyze a file to determine if it's a Bitcoin wallet
arguments:
  - name: file
    description: Path to file to analyze
    required: true
---

# Detect Bitcoin Wallet

Analyze a file to determine if it's a Bitcoin wallet.dat file.

## Execution

```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 lib/wallet_detector.py "$file"
```

## Detection Method

The detector analyzes:

1. **File Header** - Checks for Berkeley DB magic bytes
   - Version 4.x: `\x00\x05\x31\x62`
   - Version 5.x: `\x00\x05\x32\x62`
   - Version 6.x: `\x00\x06\x31\x62`

2. **Content Patterns** - Searches for Bitcoin-specific strings:
   - `defaultkey` - Default wallet key
   - `bestblock` - Blockchain sync state
   - `pool` - Key pool
   - `key`, `wkey`, `ckey`, `mkey` - Various key types

3. **Structure Analysis** - Validates Berkeley DB page structure

## Output

Returns:
- **Is Wallet**: Boolean (True if confidence >= 40%)
- **Confidence**: 0-100% score
- **Details**: Which patterns were detected

## Confidence Scoring

| Score | Interpretation |
|-------|----------------|
| 80-100% | Definitely a Bitcoin wallet |
| 50-79% | Very likely a Bitcoin wallet |
| 40-49% | Possibly a Bitcoin wallet |
| 0-39% | Probably not a Bitcoin wallet |

## Next Steps

If a wallet is detected, use `/recover-wallet` to extract keys and check balances.
