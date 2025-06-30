# Security Guide

## 🔒 Critical Security Information

This tool extracts **private keys** - the cryptographic secrets that control Bitcoin. Anyone with these keys can steal your funds. Treat them like cash or passwords.

## Before You Start

### 1. Work on a Secure Computer
- Use a trusted computer, not a public/shared one
- Ensure your system is malware-free
- Consider disconnecting from the internet while handling keys

### 2. Create Backups
```bash
cp wallet.dat wallet.dat.backup
```
Never work on your only copy!

### 3. Use Encrypted Storage
If possible, work on an encrypted drive:
- **Windows**: BitLocker
- **macOS**: FileVault
- **Linux**: LUKS/dm-crypt

## During Recovery

### Handle Private Keys Safely

**DO:**
- ✅ Keep private keys local only
- ✅ Use secure connections (HTTPS) when checking balances
- ✅ Delete temporary files immediately after use
- ✅ Use strong passwords for encrypted exports

**DON'T:**
- ❌ Email private keys
- ❌ Save to cloud storage (Dropbox, Google Drive, etc.)
- ❌ Post screenshots online
- ❌ Share keys with "support" (no legitimate service asks for keys)
- ❌ Use online "wallet recovery" services

### Monitor for Suspicious Activity

Watch for:
- Unexpected network connections
- Clipboard monitoring software
- Keyloggers
- Screen recording malware

## After Recovery

### 1. Transfer Funds Immediately
Don't leave funds in addresses where private keys have been exposed on your computer.

```bash
# Good practice: Test with small amount first
Send 0.001 BTC → Verify receipt → Send remainder
```

### 2. Secure Deletion

**Standard deletion is NOT enough!** Deleted files can be recovered.

#### Linux/macOS
```bash
# Secure overwrite (35 passes)
shred -vfz -n 35 private_keys.txt

# Faster but still secure (3 passes)
shred -vfz -n 3 private_keys.txt

# Wipe free space
# Linux
dd if=/dev/urandom of=tempfile bs=1M; rm tempfile

# macOS
diskutil secureErase freespace 3 /Volumes/YourDrive
```

#### Windows
```powershell
# Single file
cipher /w:C:\path\to\file

# Entire directory
cipher /w:C:\path\to\directory

# SDelete tool (download from Microsoft)
sdelete -p 3 -s -z C:\path\to\directory
```

### 3. Clear System Traces

#### Clear clipboard
```python
# Python
import pyperclip
pyperclip.copy('')

# Or just copy some random text
```

#### Clear terminal history
```bash
# Bash
history -c
rm ~/.bash_history

# PowerShell
Clear-History
Remove-Item (Get-PSReadlineOption).HistorySavePath
```

#### Clear swap files
```bash
# Linux
sudo swapoff -a
sudo swapon -a

# Windows (requires admin)
cipher /w:C:\
```

## Secure Storage Best Practices

### For Active Trading (< $1,000)
- Hardware wallet (Ledger, Trezor)
- Mobile wallet with strong PIN
- Reputable exchange with 2FA

### For Long-term Storage (> $1,000)
1. **Hardware Wallet** (recommended)
   - Ledger Nano X/S
   - Trezor Model T/One
   - BitBox02
   - Coldcard

2. **Paper Wallet** (advanced users)
   - Generated offline
   - BIP38 encrypted
   - Multiple copies in secure locations

3. **Multi-signature Setup** (maximum security)
   - 2-of-3 or 3-of-5 setup
   - Keys in different locations
   - One key in safety deposit box

## Red Flags / Scam Warnings

### Never Trust:
- 🚫 "Wallet recovery services" asking for private keys
- 🚫 Emails claiming to be from exchanges
- 🚫 "Double your Bitcoin" schemes
- 🚫 Random DMs offering help
- 🚫 Software requiring admin rights to "recover" wallets
- 🚫 Websites asking you to enter private keys

### Common Scams:
1. **Fake Support**: Scammers posing as support staff
2. **Phishing Sites**: Lookalike exchange websites
3. **Malicious Software**: "Wallet recovery tools" that steal
4. **Social Engineering**: Building trust then asking for keys

## Emergency Response

### If You Suspect Compromise:

1. **Immediately transfer funds** to a new secure wallet
2. **Don't panic** - you have time if you act quickly
3. **Create new wallets** on a different, clean device
4. **Document everything** for potential law enforcement

### Useful Commands:
```bash
# Monitor your addresses for unauthorized transactions
watch -n 10 'curl -s https://blockchain.info/q/addressbalance/YOUR_ADDRESS'

# Check recent transactions
curl https://blockchain.info/rawaddr/YOUR_ADDRESS | jq '.txs[0:5]'
```

## Additional Resources

- [Bitcoin Security Guide](https://bitcoin.org/en/secure-your-wallet)
- [Hardware Wallet Comparison](https://bitcoin-hardware-wallet.github.io/)
- [Andreas Antonopoulos - Bitcoin Security](https://www.youtube.com/watch?v=vt-zXEsJ61U)

---

**Remember**: Bitcoin transactions are irreversible. Take security seriously - there's no "undo" button!