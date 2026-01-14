# Installing Bitcoin Wallet Recovery Plugin for Claude Code

This guide explains how to install and use the Bitcoin Wallet Recovery plugin with Claude Code.

## Prerequisites

- **Claude Code** CLI installed ([claude.ai/code](https://claude.ai/code))
- **Python 3.7+**
- **Berkeley DB libraries** (platform-specific, see below)

## Quick Install (2 Commands)

### Step 1: Add the Marketplace

```bash
/plugin marketplace add josh-stephens/simple-bitcoin-wallet-recovery
```

### Step 2: Install the Plugin

```bash
/plugin install bitcoin-wallet-recovery@simple-bitcoin-wallet-recovery
```

### Step 3: Verify Installation

```bash
/plugin list
```

You should see:
```
bitcoin-wallet-recovery@simple-bitcoin-wallet-recovery (enabled)
```

## Install Python Dependencies

After plugin installation, install the required Python packages:

```bash
# Find the plugin directory
cd ~/.claude/plugins/cache/simple-bitcoin-wallet-recovery/*/

# Install dependencies
pip install -r requirements.txt
```

## Platform-Specific Setup

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install python3-bsddb3 libdb-dev python3-pip
pip install -r requirements.txt
```

### macOS

```bash
brew install berkeley-db python3
pip install bsddb3
pip install -r requirements.txt
```

### Windows

```powershell
# Install via pip (may require Visual C++ Build Tools)
pip install bsddb3
pip install -r requirements.txt
```

If `bsddb3` fails to install on Windows:
1. Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Or use WSL (Windows Subsystem for Linux) with Ubuntu

## Available Commands

After installation, these commands are available in Claude Code:

| Command | Description |
|---------|-------------|
| `/recover-wallet <path>` | Run full recovery wizard on a wallet file or directory |
| `/scan-wallets <directory>` | Scan directory for potential wallet files |
| `/detect-wallet <file>` | Check if a file is a Bitcoin wallet |
| `/check-balance <address>` | Check balance of a Bitcoin address |

## Usage Examples

### Recover from a Single Wallet

```
/recover-wallet /path/to/wallet.dat
```

### Scan a Directory

```
/scan-wallets /path/to/old/backups
```

### Check an Address Balance

```
/check-balance 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### Dry Run (Preview Only)

```
/recover-wallet /path/to/directory --dry-run
```

## Updating the Plugin

```bash
/plugin marketplace update simple-bitcoin-wallet-recovery
```

## Uninstalling

```bash
/plugin uninstall bitcoin-wallet-recovery@simple-bitcoin-wallet-recovery
/plugin marketplace remove simple-bitcoin-wallet-recovery
```

## Troubleshooting

### "bsddb3 not found" Error

Install Berkeley DB libraries for your platform (see Platform-Specific Setup above).

### "Permission denied" on Linux/macOS

The plugin sets secure file permissions (600) on exported private keys. This is intentional for security.

### API Rate Limiting

If balance checks fail, the tool implements rate limiting. Wait a few seconds and try again.

### Encrypted Wallets

If your wallet is encrypted, you'll be prompted for the password. Without the correct password, keys cannot be extracted.

## Security Notes

- **Private keys are sensitive** - Never share them or upload to cloud storage
- **Transfer immediately** - Move recovered Bitcoin to a secure wallet
- **Secure deletion** - Delete exported key files after successful transfer
- **Test first** - Send a small amount first to verify everything works

## Support

- **Issues**: [GitHub Issues](https://github.com/josh-stephens/simple-bitcoin-wallet-recovery/issues)
- **Documentation**: See `docs/` folder in the repository

## License

MIT License - See [LICENSE](../LICENSE) file.
