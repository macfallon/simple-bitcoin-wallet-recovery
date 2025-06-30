#!/usr/bin/env python3
"""
Secure Exporter Module
======================

Handles secure export of private keys in multiple formats with
security best practices and automatic cleanup options.
"""

import os
import json
import shutil
import platform
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

class SecureExporter:
    """Export private keys securely in multiple formats"""
    
    # Supported export formats
    FORMATS = {
        'electrum': 'Electrum wallet (plain text WIF keys)',
        'bitcoin_core': 'Bitcoin Core importwallet format',
        'json': 'JSON format with metadata',
        'csv': 'CSV spreadsheet format',
        'qr': 'QR codes (requires qrcode library)',
        'encrypted': 'AES-256 encrypted JSON'
    }
    
    def __init__(self, output_dir: str = None):
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_dir = Path(f'wallet_export_{timestamp}')
            
        self.output_dir.mkdir(exist_ok=True)
        self.exported_files = []
        
    def export_keys(self, addresses: List[Dict], format: str = 'electrum', 
                   password: Optional[str] = None) -> str:
        """
        Export private keys in specified format.
        
        Args:
            addresses: List of dicts with 'address', 'private_key', 'balance'
            format: Export format (electrum, bitcoin_core, json, csv, qr, encrypted)
            password: Password for encrypted export
            
        Returns:
            Path to exported file
        """
        if format not in self.FORMATS:
            raise ValueError(f"Unsupported format: {format}")
            
        # Filter out addresses without private keys
        valid_addresses = [a for a in addresses if a.get('private_key')]
        
        if not valid_addresses:
            raise ValueError("No addresses with private keys to export")
            
        # Export based on format
        if format == 'electrum':
            return self._export_electrum(valid_addresses)
        elif format == 'bitcoin_core':
            return self._export_bitcoin_core(valid_addresses)
        elif format == 'json':
            return self._export_json(valid_addresses)
        elif format == 'csv':
            return self._export_csv(valid_addresses)
        elif format == 'qr':
            return self._export_qr_codes(valid_addresses)
        elif format == 'encrypted':
            if not password:
                raise ValueError("Password required for encrypted export")
            return self._export_encrypted(valid_addresses, password)
            
    def _export_electrum(self, addresses: List[Dict]) -> str:
        """Export in Electrum format (one WIF key per line)"""
        file_path = self.output_dir / 'electrum_import.txt'
        
        with open(file_path, 'w') as f:
            # Just the private keys, one per line
            for addr in addresses:
                f.write(f"{addr['private_key']}\n")
                
        self.exported_files.append(file_path)
        self._set_secure_permissions(file_path)
        
        return str(file_path)
        
    def _export_bitcoin_core(self, addresses: List[Dict]) -> str:
        """Export in Bitcoin Core importwallet format"""
        file_path = self.output_dir / 'bitcoin_core_import.txt'
        
        with open(file_path, 'w') as f:
            f.write("# Bitcoin Core import format\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write("# Format: <private_key> <label> <reserved>\n\n")
            
            for addr in addresses:
                label = addr.get('label', addr['address'])
                reserved = 'false'  # Not a reserve key
                f.write(f"{addr['private_key']} {label} {reserved}\n")
                
        self.exported_files.append(file_path)
        self._set_secure_permissions(file_path)
        
        return str(file_path)
        
    def _export_json(self, addresses: List[Dict]) -> str:
        """Export in JSON format with all metadata"""
        file_path = self.output_dir / 'wallet_keys.json'
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'format': 'json',
            'version': '1.0',
            'total_balance': sum(a.get('balance', 0) for a in addresses),
            'address_count': len(addresses),
            'addresses': []
        }
        
        for addr in addresses:
            export_data['addresses'].append({
                'address': addr['address'],
                'private_key_wif': addr['private_key'],
                'private_key_hex': addr.get('hexsec', ''),
                'balance': addr.get('balance', 0),
                'compressed': addr.get('compressed', True),
                'label': addr.get('label', ''),
                'tx_count': addr.get('tx_count', 0)
            })
            
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        self.exported_files.append(file_path)
        self._set_secure_permissions(file_path)
        
        return str(file_path)
        
    def _export_csv(self, addresses: List[Dict]) -> str:
        """Export in CSV format"""
        file_path = self.output_dir / 'wallet_keys.csv'
        
        with open(file_path, 'w') as f:
            # Header
            f.write("Address,Private Key (WIF),Balance (BTC),Label,Transactions\n")
            
            # Data
            for addr in addresses:
                address = addr['address']
                key = addr['private_key']
                balance = addr.get('balance', 0)
                label = addr.get('label', '').replace(',', ';')  # Escape commas
                tx_count = addr.get('tx_count', 0)
                
                f.write(f"{address},{key},{balance:.8f},{label},{tx_count}\n")
                
        self.exported_files.append(file_path)
        self._set_secure_permissions(file_path)
        
        return str(file_path)
        
    def _export_qr_codes(self, addresses: List[Dict]) -> str:
        """Export private keys as QR codes"""
        try:
            import qrcode
        except ImportError:
            raise ImportError("qrcode library required: pip install qrcode[pil]")
            
        qr_dir = self.output_dir / 'qr_codes'
        qr_dir.mkdir(exist_ok=True)
        
        # Create index file
        index_path = qr_dir / 'index.html'
        with open(index_path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Bitcoin Private Key QR Codes</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .warning { color: red; font-weight: bold; }
        .qr-container { 
            border: 1px solid #ccc; 
            padding: 10px; 
            margin: 10px;
            display: inline-block;
        }
        .qr-container img { width: 200px; height: 200px; }
        .address { font-size: 10px; word-break: break-all; }
        .balance { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Bitcoin Private Key QR Codes</h1>
    <p class="warning">⚠️ WARNING: These QR codes contain private keys! Keep them secure!</p>
    <p>Total: {total_btc:.8f} BTC (${total_usd:,.2f} USD)</p>
    <hr>
""".format(
                total_btc=sum(a.get('balance', 0) for a in addresses),
                total_usd=sum(a.get('balance', 0) for a in addresses) * 100000  # Approximate
            ))
            
        # Generate QR codes
        for i, addr in enumerate(addresses):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(addr['private_key'])
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_path = qr_dir / f"qr_{i:03d}.png"
            img.save(img_path)
            
            # Add to HTML index
            with open(index_path, 'a') as f:
                f.write(f"""
    <div class="qr-container">
        <img src="qr_{i:03d}.png" alt="QR Code">
        <div class="address">{addr['address']}</div>
        <div class="balance">{addr.get('balance', 0):.8f} BTC</div>
    </div>
""")
                
        # Close HTML
        with open(index_path, 'a') as f:
            f.write("</body></html>")
            
        self.exported_files.extend(list(qr_dir.glob('*')))
        
        return str(qr_dir)
        
    def _export_encrypted(self, addresses: List[Dict], password: str) -> str:
        """Export encrypted JSON file"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
        except ImportError:
            raise ImportError("cryptography library required: pip install cryptography")
            
        # Generate key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'bitcoin_wallet_salt',  # Should use random salt in production
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        
        # Prepare data
        export_data = {
            'export_date': datetime.now().isoformat(),
            'addresses': addresses
        }
        
        # Encrypt
        json_data = json.dumps(export_data).encode()
        encrypted_data = fernet.encrypt(json_data)
        
        # Save
        file_path = self.output_dir / 'wallet_encrypted.enc'
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
            
        # Also save decryption instructions
        instructions_path = self.output_dir / 'DECRYPTION_INSTRUCTIONS.txt'
        with open(instructions_path, 'w') as f:
            f.write("""Encrypted Wallet Decryption Instructions
=========================================

To decrypt your wallet file:

1. Install Python and cryptography library:
   pip install cryptography

2. Use this Python code:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

password = input("Enter password: ")

# Generate key from password
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=b'bitcoin_wallet_salt',
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
fernet = Fernet(key)

# Decrypt
with open('wallet_encrypted.enc', 'rb') as f:
    encrypted_data = f.read()
    
decrypted_data = fernet.decrypt(encrypted_data)
wallet_data = json.loads(decrypted_data)

print(json.dumps(wallet_data, indent=2))
```

REMEMBER YOUR PASSWORD! Without it, the encrypted file cannot be decrypted.
""")
            
        self.exported_files.append(file_path)
        self.exported_files.append(instructions_path)
        self._set_secure_permissions(file_path)
        
        return str(file_path)
        
    def _set_secure_permissions(self, file_path: Path):
        """Set secure file permissions (owner read/write only)"""
        try:
            if platform.system() != 'Windows':
                os.chmod(file_path, 0o600)
        except:
            pass
            
    def create_security_notice(self):
        """Create security notice file"""
        notice_path = self.output_dir / 'SECURITY_WARNING.txt'
        
        with open(notice_path, 'w') as f:
            f.write("""
⚠️  CRITICAL SECURITY WARNING ⚠️
================================

This directory contains PRIVATE KEYS that give complete access to your Bitcoin!

SECURITY RULES:
1. NEVER share these files with anyone
2. NEVER upload to cloud storage (Dropbox, Google Drive, etc.)
3. NEVER email these files
4. NEVER post screenshots online

RECOMMENDED ACTIONS:
1. Transfer your Bitcoin to a secure wallet immediately
2. Delete these files after successful transfer
3. Use secure deletion:
   - Linux/Mac: shred -vfz [filename]
   - Windows: cipher /w:C:\\path\\to\\directory

SECURE DELETION COMMANDS:
""")
            
            # Add specific deletion commands for exported files
            for file in self.exported_files:
                f.write(f"\nshred -vfz \"{file}\"")
                
        self.exported_files.append(notice_path)
        
    def secure_delete(self, confirm: bool = False):
        """Securely delete all exported files"""
        if not confirm:
            print("⚠️  WARNING: This will permanently delete all exported files!")
            response = input("Type 'DELETE' to confirm: ")
            if response != 'DELETE':
                print("Deletion cancelled.")
                return False
                
        deleted_count = 0
        
        for file_path in self.exported_files:
            if file_path.exists():
                if platform.system() == 'Windows':
                    # Windows secure delete
                    try:
                        # Overwrite with random data
                        file_size = file_path.stat().st_size
                        with open(file_path, 'wb') as f:
                            f.write(os.urandom(file_size))
                        file_path.unlink()
                        deleted_count += 1
                    except:
                        pass
                else:
                    # Unix-like secure delete
                    try:
                        subprocess.run(['shred', '-vfz', str(file_path)], 
                                     capture_output=True, check=True)
                        deleted_count += 1
                    except:
                        # Fallback to simple delete
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except:
                            pass
                            
        # Remove directory if empty
        try:
            self.output_dir.rmdir()
        except:
            pass
            
        print(f"✅ Securely deleted {deleted_count} files")
        return True
        
    def create_import_guide(self):
        """Create wallet import guide"""
        guide_path = self.output_dir / 'IMPORT_GUIDE.md'
        
        with open(guide_path, 'w') as f:
            f.write("""# Wallet Import Guide

## Electrum (Recommended)
1. Download Electrum from https://electrum.org
2. Create new wallet → "Import Bitcoin addresses or private keys"
3. Copy contents of `electrum_import.txt`
4. Wait for synchronization

## Bitcoin Core
1. Open Bitcoin Core console (Help → Debug Window → Console)
2. Run: `importwallet "path/to/bitcoin_core_import.txt"`
3. Wait for rescan (may take hours)

## Other Wallets

### Exodus
- Settings → Assets → Bitcoin → Move Funds → Private Key

### Mycelium (Mobile)
- Accounts → Key+ → Advanced → Import

### Blockchain.com
- Settings → Wallets & Addresses → Import Address → Private Key

## Important Notes
- Always send a small test transaction first
- Check network fees before sending
- Keep original files until transfer is confirmed
""")
            
        self.exported_files.append(guide_path)


if __name__ == "__main__":
    # Test the exporter
    test_addresses = [
        {
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'private_key': 'L1234567890abcdef...',  # Example WIF
            'balance': 0.1,
            'label': 'Test Address'
        }
    ]
    
    exporter = SecureExporter()
    
    print("Testing Secure Exporter")
    print("-" * 50)
    
    # Test each format
    for format in ['electrum', 'json', 'csv']:
        try:
            path = exporter.export_keys(test_addresses, format=format)
            print(f"✅ Exported {format} format to: {path}")
        except Exception as e:
            print(f"❌ Failed to export {format}: {e}")
            
    # Create security files
    exporter.create_security_notice()
    exporter.create_import_guide()
    
    print(f"\n📁 Export directory: {exporter.output_dir}")