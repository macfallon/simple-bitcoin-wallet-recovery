# Guide: Transferring Bitcoin to Coinbase

## Verified Balance Summary
- **Total Bitcoin**: 0.12145281 BTC  
- **Status**: ✅ All balances verified across 3 blockchain explorers

## Your Funded Addresses
1. `13cHqB1vTx94NNxom8NwHgFfn6E7bnmnTq` (Slush): 0.04179530 BTC
2. `1Nf4xvHEBcxUoZXRp9Fi6QrUp1TCK7wcDk` (Eclipse): 0.04014620 BTC
3. `19rNsCg6BgpuZWJTAWB9kkhrj8QqfycdpD`: 0.02904965 BTC
4. `19tpvtWxQ3cc7L3rWJqGiZbC9akEnLv2k7`: 0.01019683 BTC
5. `1F2fvzHoL9jCSRxz5W1oa3mZUeyQKLmQhT`: 0.00026483 BTC

## Method 1: Direct Transfer (Recommended)
This method uses a software wallet to send Bitcoin directly to Coinbase.

### Step 1: Get Your Coinbase Deposit Address
1. Log into Coinbase
2. Navigate to "Portfolio" → "Bitcoin"
3. Click "Receive"
4. Copy your Bitcoin deposit address

### Step 2: Import Private Keys to a Software Wallet
Use one of these wallets:

#### Option A: Electrum (Recommended)
1. Download Electrum from https://electrum.org
2. Create new wallet → "Import Bitcoin addresses or private keys"
3. Paste the private keys from `private_keys_for_import.txt`
4. Wait for synchronization

#### Option B: Bitcoin Core
1. Open Bitcoin Core console
2. For each private key, run: `importprivkey "YOUR_PRIVATE_KEY" "label" false`
3. After all keys, run: `rescanblockchain`

### Step 3: Send to Coinbase
1. Create a new transaction
2. Send to your Coinbase deposit address
3. **Important**: Send a small test amount first (e.g., 0.001 BTC)
4. After confirming receipt, send the remaining balance

## Method 2: Coinbase Wallet Import (If Available)
Some regions allow direct private key import:

1. In Coinbase, look for "Import Wallet" option
2. Select "Import with private key"
3. Import keys one by one from `private_keys_for_import.txt`

## Important Considerations

### Transaction Fees
- Current network fees: Check https://mempool.space
- Budget ~$5-20 for transaction fees
- Use "Normal" priority unless urgent

### Security Best Practices
1. **Before Transfer**:
   - Verify Coinbase deposit address multiple times
   - Consider using a hardware wallet as intermediary
   - Make sure your Coinbase account has 2FA enabled

2. **During Transfer**:
   - Start with a test transaction
   - Double-check addresses (compare first/last 4 characters)
   - Save transaction IDs

3. **After Transfer**:
   - Delete all private key files
   - Secure wipe if possible: `shred -vfz private_keys_for_import.txt`
   - Keep transaction records for taxes

### Tax Implications
- These Bitcoin may have tax obligations
- In the US: Report as capital gains
- Keep records of:
  - Original acquisition date (if known)
  - Original cost basis
  - Transfer date and BTC price
  - Coinbase sale price

## Troubleshooting

**"Invalid private key" error**:
- Ensure you're copying the WIF format key (starts with 'K' or 'L')
- Check for extra spaces or line breaks

**Transaction not confirming**:
- Check fee amount on https://mempool.space
- May need to wait or increase fee

**Balance not showing in wallet**:
- Wait for full synchronization
- For Electrum: View → Show Addresses
- Verify addresses match

## Need Help?
- Electrum Support: https://electrum.org/#community
- Coinbase Support: https://help.coinbase.com
- Bitcoin Stack Exchange: https://bitcoin.stackexchange.com

---
⚠️ **Final Security Reminder**: After successful transfer, securely delete all private key files!