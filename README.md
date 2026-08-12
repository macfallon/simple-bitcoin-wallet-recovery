# 🔑 Simple Bitcoin Wallet Recovery

> **Success Story**: In December 2024, I found an old `wallet.dat` file on a backup drive. Using these tools, I successfully recovered **0.12145281 BTC**! This project packages everything I learned into an easy-to-use tool so you can do the same.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What This Tool Does

Have you found an old `wallet.dat` file and wonder if it contains Bitcoin? This tool helps you:

1. **Detect** if any `.dat` file is actually a Bitcoin wallet
2. **Extract** all Bitcoin addresses and private keys
3. **Check** current balances across multiple blockchain APIs
4. **Export** private keys for importing into modern wallets
5. **Transfer** your Bitcoin safely to exchanges or hardware wallets

## 🚀 Quick Start

### Option 1: Claude Code Plugin (Recommended)

If you use [Claude Code](https://claude.ai/code), install as a plugin:

```bash
# Add the marketplace
/plugin marketplace add josh-stephens/simple-bitcoin-wallet-recovery

# Install the plugin
/plugin install bitcoin-wallet-recovery@bitcoin-recovery-tools
```

Then use commands like `/recover-wallet /path/to/wallet.dat`

See [Plugin Installation Guide](docs/PLUGIN_INSTALL.md) for details.

### Option 2: Standalone Installation

```bash
# Clone the repository
git clone https://github.com/josh-stephens/simple-bitcoin-wallet-recovery.git
cd simple-bitcoin-wallet-recovery

# Install dependencies
pip3 install -r requirements.txt
```

### Basic Usage

```bash
# Scan an entire drive or directory (recommended)
python3 recovery_wizard.py --scandir /mnt/c

# Check a single wallet file
python3 recovery_wizard.py wallet.dat

# Dry run to see what would be scanned
python3 recovery_wizard.py --scandir /path/to/old/backups/ --dry-run
```

## 📖 Detailed Usage Guide

### Step 1: Find Your Wallet Files

Common locations for old Bitcoin wallets:
- `C:\Users\[Username]\AppData\Roaming\Bitcoin\` (Windows)
- `~/Library/Application Support/Bitcoin/` (Mac)
- `~/.bitcoin/` (Linux)
- Old backup drives, USB sticks, or cloud storage
- Files named `wallet.dat` or any `.dat` file from 2009-2017

### Step 2: Run the Recovery Wizard

**Recommended: Scan a Directory**
```bash
python3 recovery_wizard.py --scandir /mnt/c
```

This will:
1. Recursively scan for all .dat files
2. Show progress with file count and progress bar
3. Analyze each .dat file to identify Bitcoin wallets
4. Extract private keys from confirmed wallets
5. Check balances across multiple blockchain APIs
6. Generate organized output in `bitcoin_recovery_[timestamp]/`

**Alternative: Check Single File**
```bash
python3 recovery_wizard.py suspicious_file.dat
```

### Step 3: Check Your Results

The tool creates an organized output directory:
```
bitcoin_recovery_20241229_143022/
├── output/
│   ├── summary_report.txt        # Overview of all findings
│   ├── funded_wallets/          # Wallets with Bitcoin
│   │   └── wallet_001/
│   │       ├── private_keys.txt # Keys for import
│   │       └── TRANSFER_GUIDE.txt
│   └── empty_wallets/           # Wallets without Bitcoin
└── scratch/                     # Temporary files (can delete)
```

If Bitcoin is found, you'll see:
```
🎉 SUCCESS! Found 0.12145281 BTC!
📁 Check bitcoin_recovery_[timestamp]/output/funded_wallets/ for private keys
📄 See bitcoin_recovery_[timestamp]/output/summary_report.txt for details
```

### Step 4: Transfer Your Bitcoin

1. **Install Electrum** from https://electrum.org
2. Create new wallet → "Import Bitcoin addresses or private keys"
3. Copy the private keys from `funded_private_keys.txt`
4. Send to your Coinbase/Kraken/hardware wallet

**Important**: Always send a small test transaction first!

## 🔧 Advanced Features

### Directory Scanning Options
```bash
# Scan with progress tracking
python3 recovery_wizard.py --scandir ~/old-computers/

# Dry run to preview what will be scanned
python3 recovery_wizard.py --scandir /mnt/backup --dry-run

# Quiet mode for automation
python3 recovery_wizard.py --scandir /mnt/c --quiet
```

### Export Formats
```python
from lib.secure_exporter import SecureExporter

exporter = SecureExporter()
exporter.export_keys(addresses, format='electrum')  # For Electrum
exporter.export_keys(addresses, format='bitcoin_core')  # For Bitcoin Core
exporter.export_keys(addresses, format='csv')  # Spreadsheet
```

### Custom Balance Checking
```python
from lib.balance_checker import BalanceChecker

checker = BalanceChecker()
balance = checker.check_balance('1YourBitcoinAddress...')
```

## 🛡️ Security Best Practices

1. **Never share private keys** - Anyone with these keys can steal your Bitcoin
2. **Work offline when possible** - Disconnect internet when handling private keys
3. **Delete files securely** after transferring:
   ```bash
   # Linux/Mac
   shred -vfz private_keys_file.txt
   
   # Windows  
   cipher /w:C:\path\to\directory
   ```
4. **Use 2FA** on any exchange accounts
5. **Consider a hardware wallet** for long-term storage

## 🔍 How It Works

1. **Wallet Detection**: Analyzes file headers and structure to identify Bitcoin wallets
2. **Key Extraction**: Uses modified PyWallet to extract private keys
3. **Balance Checking**: Queries multiple blockchain APIs for reliability
4. **Secure Export**: Provides keys in formats compatible with modern wallets

## 📋 Requirements

- Python 3.7+
- Berkeley DB libraries
- Internet connection for balance checking

### Ubuntu/Debian
```bash
sudo apt-get install python3-bsddb3 libdb-dev
pip3 install -r requirements.txt
```

### macOS
```bash
brew install berkeley-db
pip3 install -r requirements.txt
```

### Windows
See [detailed Windows instructions](docs/WINDOWS_INSTALL.md)

## 🐛 Troubleshooting

### "bsddb module not found"
Install Berkeley DB: `sudo apt-get install python3-bsddb3`

### "Permission denied"
Run with appropriate permissions or check file ownership

### "No balance found"
- Wallet might be empty (funds already moved)
- Try running again (API rate limits)
- Check internet connection

### Large wallets (1000+ addresses)
The tool handles these automatically but checking may take 10-15 minutes

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## 📜 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- Original [PyWallet](https://github.com/jackjack-jj/pywallet) by jackjack
- Blockchain APIs: blockchain.info, blockstream.info, blockcypher.com
- The Bitcoin community for years of development

## ⚠️ Disclaimer

This tool is provided as-is for educational and recovery purposes. Always verify results independently and never trust any single tool with significant funds. The authors are not responsible for any loss of funds.

---

**Found this helpful?** Consider starring ⭐ the repository!

**Recovered Bitcoin?** Share your success story (keep amounts private)!

**Need help?** Open an issue or check existing discussions.