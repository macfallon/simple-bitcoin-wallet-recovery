# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### "bsddb module not found" or "pywallet needs 'bsddb' package"

This is the most common issue. The tool requires Berkeley DB to read wallet files.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-bsddb3 libdb-dev
pip3 install bsddb3
```

**macOS:**
```bash
brew install berkeley-db
export CFLAGS="-I$(brew --prefix berkeley-db)/include"
export LDFLAGS="-L$(brew --prefix berkeley-db)/lib"
pip3 install bsddb3
```

**Windows:**
See [Windows Installation Guide](WINDOWS_INSTALL.md)

#### "has_key() not defined" or AttributeError

This happens with the original PyWallet on Python 3. Our version includes fixes for this.

### Wallet Detection Issues

#### "Not a Bitcoin wallet" but you're sure it is

1. **Check file size**: Wallets are typically > 50KB
   ```bash
   ls -lh wallet.dat
   ```

2. **Check file type**:
   ```bash
   file wallet.dat
   ```
   Should show "Berkeley DB" or similar

3. **Try forcing detection**:
   ```python
   python3 pywallet.py --wallet=yourfile.dat --dumpwallet
   ```

#### Corrupted wallet files

If you get "ERROR parsing wallet.dat", the file may be corrupted. Try:

1. Make a backup first
2. Use Bitcoin Core's salvage option
3. Try our recovery with `--recover` flag (coming soon)

### Balance Checking Issues

#### "No addresses with balance found" but you expect Bitcoin

1. **Wallet might be old**: Funds may have been moved years ago

2. **API rate limits**: Wait a few minutes and try again

3. **Check specific addresses manually**:
   - Copy an address from the output
   - Check on https://blockchair.com/bitcoin

4. **Network issues**: Ensure you have internet connectivity

#### "Error checking batch" messages

This usually means API rate limiting. The tool will retry automatically.

### Export Issues

#### "Permission denied" when creating files

**Linux/Mac:**
```bash
chmod 755 .
```

**Windows:**
Run as Administrator or check folder permissions

#### Can't import into Electrum

1. Ensure you're copying the exact private key format (WIF)
2. Remove any extra spaces or line breaks
3. Try importing one key at a time

### Large Wallet Issues

#### Checking takes forever (1000+ addresses)

This is normal for large wallets. The tool checks in batches to avoid API limits.

- Expect ~5-10 minutes for 1000 addresses
- Progress is shown as "X/Y addresses checked"
- Results are cached, so re-running is faster

#### "Memory error" with huge wallets

For wallets with 10,000+ addresses:

```bash
# Increase Python memory limit
ulimit -v unlimited
python3 recovery_wizard.py large_wallet.dat
```

### Security Warnings

#### "Cannot import: wallet is encrypted"

If PyWallet reports the wallet is encrypted, you'll need the password:

```bash
python3 pywallet.py --wallet=encrypted.dat --passphrase="YourPassword" --dumpwallet
```

#### Antivirus flags the tool

Some antivirus software flags cryptocurrency tools. This is a false positive because:
- We're open source
- No network activity except blockchain API calls
- No code obfuscation

Add an exception or run on an isolated system.

### Platform-Specific Issues

#### Windows: "Cannot find vcvarsall.bat"

Install Visual Studio Build Tools:
https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

#### macOS: "Library not loaded"

```bash
brew reinstall berkeley-db python@3.11
```

#### Linux: "No module named _bsddb"

```bash
sudo apt-get install python3-dev
pip3 install --force-reinstall bsddb3
```

### Getting Help

If you're still stuck:

1. **Check existing issues**: https://github.com/yourusername/simple-bitcoin-wallet-recovery/issues

2. **Enable debug mode**:
   ```bash
   python3 recovery_wizard.py --debug wallet.dat
   ```

3. **Create an issue** with:
   - Your OS and Python version
   - Complete error message
   - Size of wallet file
   - Steps you've tried

### Emergency Recovery

If the tool fails but you need immediate access:

1. **Try Electrum directly**: Sometimes it can import wallet.dat files

2. **Use Bitcoin Core**: The original client can always read its own wallets

3. **Professional recovery**: For significant amounts, consider professional services

Remember: Your private keys are in the wallet file. As long as you have the file and any password, your Bitcoin is recoverable!