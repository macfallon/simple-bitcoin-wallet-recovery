# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Simple Bitcoin Wallet Recovery is a user-friendly tool for recovering Bitcoin from old wallet.dat files. Born from a real success story of recovering 0.12145281 BTC from a forgotten wallet, it streamlines the complex process into a simple wizard.

## Project Structure

```
simple-bitcoin-wallet-recovery/
├── recovery_wizard.py      # Main entry point - orchestrates the recovery process
├── pywallet.py            # Modified PyWallet core for wallet reading
├── lib/
│   ├── wallet_detector.py  # Analyzes .dat files to identify Bitcoin wallets
│   ├── balance_checker.py  # Multi-source blockchain API balance verification
│   └── secure_exporter.py  # Secure private key export in multiple formats
├── docs/
│   ├── TROUBLESHOOTING.md  # Common issues and solutions
│   └── SECURITY.md         # Security best practices
└── [legacy scripts]        # Original recovery scripts kept for reference
```

## Key Commands

### Setup and Dependencies

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y python3-bsddb3 libdb-dev

# Install Python packages
pip3 install -r requirements.txt

# Quick install
pip3 install bsddb3 ecdsa requests
```

### Running the Tool

```bash
# Basic wallet recovery
python3 recovery_wizard.py wallet.dat

# Scan directory for wallets
python3 recovery_wizard.py --scan /path/to/directory/

# Direct wallet dump (legacy)
python3 pywallet.py --wallet=wallet.dat --dumpwallet
```

### Development and Testing

```bash
# Run tests
pytest tests/

# Check code style
black --check .
flake8 .

# Format code
black .
```

## Architecture and Key Components

### 1. Recovery Wizard (`recovery_wizard.py`)
- Main orchestrator that guides users through the recovery process
- Handles user interaction and progress display
- Coordinates between detector, extractor, checker, and exporter modules
- Implements graceful error handling and recovery

### 2. Wallet Detector (`lib/wallet_detector.py`)
- **Universal .dat file analysis** - can identify Bitcoin wallets even if renamed
- Berkeley DB header detection for multiple versions
- Pattern matching for wallet-specific data structures
- Confidence scoring system (0-100%)
- Batch directory scanning capabilities

### 3. Balance Checker (`lib/balance_checker.py`)
- **Multi-source verification** across 4+ blockchain APIs
- Intelligent retry logic with exponential backoff
- Response caching to minimize API calls
- Consensus algorithm for balance verification
- Handles rate limiting gracefully

### 4. Secure Exporter (`lib/secure_exporter.py`)
- Multiple export formats: Electrum, Bitcoin Core, JSON, CSV, QR codes
- Secure file permissions (600 on Unix)
- Optional encryption with AES-256
- Secure deletion utilities
- Automatic security warnings and guides

### 5. PyWallet Core (`pywallet.py`)
- Modified for Python 3 compatibility
- Key changes from original:
  - `has_key()` → `in` operator (lines 2689, 2706)
  - Added `BytesEncoder` class for JSON serialization
  - Better error handling and reporting

## Important Implementation Details

### Python 3 Compatibility
The codebase has been updated for Python 3.7+ compatibility:
- Byte string handling with proper encoding/decoding
- Modern exception syntax
- Type hints in newer modules
- f-strings for formatting

### Security Considerations
- Private keys are handled in memory and written to disk with restrictive permissions
- All exported files include security warnings
- Temporary files are securely deleted when possible
- No network activity except blockchain API calls for balance checking

### API Rate Limiting
Balance checker implements smart rate limiting:
- Blockchain.info: 100 addresses per call, 1 second delay
- Blockstream: Single address, 0.25 second delay
- BlockCypher: Single address, 0.33 second delay
- Mempool.space: Single address, 0.1 second delay

### Error Recovery
- Wallet detection continues even if some files fail
- Balance checking retries failed APIs with others
- Partial recovery possible for corrupted wallets
- All errors are logged with helpful messages

## Common Development Tasks

### Adding a New Blockchain API
1. Add API configuration to `APIS` dict in `balance_checker.py`
2. Implement `_parse_[api_name]()` method
3. Add to consensus algorithm
4. Update documentation

### Adding Export Format
1. Add format to `FORMATS` dict in `secure_exporter.py`
2. Implement `_export_[format]()` method
3. Update security warnings if needed
4. Add format to documentation

### Improving Wallet Detection
1. Add new patterns to `WALLET_PATTERNS` in `wallet_detector.py`
2. Update confidence scoring algorithm
3. Test with various wallet versions
4. Document new detection capabilities

## Testing Approach

### Unit Tests
- Each module has independent test coverage
- Mock blockchain API responses for consistent testing
- Test edge cases (corrupted files, API failures, etc.)

### Integration Tests
- Full recovery workflow with test wallets
- Multi-format export verification
- Performance tests for large wallets (1000+ addresses)

### Security Tests
- Verify secure file permissions
- Test secure deletion functionality
- Validate no sensitive data in logs

## Performance Considerations

- Large wallets (1000+ addresses) are processed in batches
- API responses are cached to disk with 1-hour TTL
- Berkeley DB operations are read-only for safety
- Memory usage is O(n) with number of addresses

## Future Enhancements Planned

1. **Wallet corruption recovery** - Partial extraction from damaged files
2. **Multi-wallet management** - Handle multiple wallets in one session
3. **Real-time notifications** - Watch addresses for new transactions
4. **Hardware wallet integration** - Direct export to Ledger/Trezor
5. **GUI version** - Electron or PyQt interface