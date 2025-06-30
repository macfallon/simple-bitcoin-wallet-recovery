# Safe Test Wallet Creation Instructions

This wallet needs to be created using one of these methods:

## Option 1: Synthetic Wallet (Recommended)
1. Use pywallet to create a new wallet with fresh keys
2. No blockchain history = no privacy concerns
3. Perfect for demonstrations

## Option 2: Bitcoin Testnet
1. Create a testnet wallet
2. Get free testnet coins from a faucet
3. Zero cost, zero privacy risk
4. Shows real blockchain interaction

## Option 3: Minimal Mainnet Wallet
1. Create fresh Bitcoin Core wallet
2. Generate 5-10 addresses
3. Send 0.00001 BTC to one address
4. Wait for confirmation
5. Use immediately (minimal history)

## Why Not Use Existing Wallets?
- Blockchain history is permanent
- Transaction patterns can reveal personal information
- Address clustering can link to other wallets
- Even emptied wallets pose privacy risks

## Implementation Steps:
```python
# 1. Create new wallet with Bitcoin Core
bitcoin-cli createwallet "test_demo_wallet"

# 2. Generate a few addresses  
bitcoin-cli -rpcwallet=test_demo_wallet getnewaddress
bitcoin-cli -rpcwallet=test_demo_wallet getnewaddress
bitcoin-cli -rpcwallet=test_demo_wallet getnewaddress

# 3. Export wallet file
# Location: ~/.bitcoin/wallets/test_demo_wallet/wallet.dat

# 4. Copy to project
cp ~/.bitcoin/wallets/test_demo_wallet/wallet.dat ./tests/demo_wallet.dat

# 5. Add warning labels
```

## Security Notice
NEVER use a wallet that has held significant funds or has extensive transaction history as a public example.