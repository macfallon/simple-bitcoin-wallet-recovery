---
name: check-balance
description: Check Bitcoin balance for an address using multiple blockchain APIs
arguments:
  - name: address
    description: Bitcoin address to check (legacy, P2SH, or bech32 format)
    required: true
---

# Check Bitcoin Address Balance

Query multiple blockchain APIs to check the balance of a Bitcoin address.

## Supported Address Formats

- **Legacy P2PKH**: Starts with `1` (e.g., `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`)
- **P2SH**: Starts with `3` (e.g., `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy`)
- **Native SegWit**: Starts with `bc1` (e.g., `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq`)

## Execution

```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 -c "
from lib.balance_checker import check_balance
result = check_balance('$address')
print(f'Address: $address')
if result.get('error'):
    print(f'Error: {result[\"error\"]}')
else:
    print(f'Balance: {result[\"balance\"]:.8f} BTC')
    print(f'Transactions: {result.get(\"tx_count\", 0)}')
    print(f'Verified: {result.get(\"verified\", False)}')
    print(f'Sources: {result.get(\"sources\", [])}')
"
```

## APIs Used

Balance is checked across multiple sources for reliability:
1. **blockchain.info** - Primary, supports batch queries
2. **blockstream.info** - Verification source
3. **blockcypher.com** - Additional verification
4. **mempool.space** - Real-time mempool data

Results use median consensus when APIs disagree.

## Caching

Results are cached for 1 hour in `.balance_cache/` directory to reduce API calls.
