#!/usr/bin/env python3
"""
Wallet Detector Module
======================

Analyzes .dat files to determine if they are Bitcoin wallets.
Supports multiple wallet versions and provides confidence scoring.
"""

import os
import struct
from typing import Tuple, Dict, Optional

class WalletDetector:
    """Detects and analyzes potential Bitcoin wallet files"""
    
    # Berkeley DB magic bytes for different versions
    BERKELEY_DB_MAGIC = {
        b'\x00\x05\x31\x62': 'BDB 4.x',  # Bitcoin Core < 0.8
        b'\x00\x06\x15\x61': 'BDB 5.x',  # Bitcoin Core 0.8+
        b'\x00\x09\x00\x00': 'BDB 6.x',  # Newer versions
        b'\x62\x31\x05\x00': 'BDB 4.x (LE)',  # Little endian
        b'\x61\x15\x06\x00': 'BDB 5.x (LE)',
    }
    
    # Wallet-specific patterns to look for
    WALLET_PATTERNS = [
        b'defaultkey',
        b'bestblock',
        b'pool',
        b'key',
        b'wkey',
        b'ckey',
        b'mkey',
        b'name',
        b'purpose',
        b'hdchain',
        b'version',
        b'minversion',
        b'settings',
        b'tx',
        b'\x04\x6b\x65\x79\x41',  # "keyA" in hex
        b'Bitcoin',
        b'wallet.dat'
    ]
    
    # File size expectations
    MIN_WALLET_SIZE = 1024  # 1KB minimum
    TYPICAL_MIN_SIZE = 50 * 1024  # 50KB typical minimum
    
    def __init__(self):
        self.file_path = None
        self.file_size = 0
        self.is_berkeley_db = False
        self.db_version = None
        self.pattern_matches = []
        self.confidence = 0
        
    def analyze_file(self, file_path: str) -> Tuple[bool, int, Optional[Dict]]:
        """
        Analyze a file to determine if it's a Bitcoin wallet.
        
        Returns:
            tuple: (is_wallet, confidence_percentage, wallet_info)
        """
        self.file_path = file_path
        self.confidence = 0
        wallet_info = {}
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, 0, None
            
        # Get file size
        self.file_size = os.path.getsize(file_path)
        
        # Size checks
        if self.file_size < self.MIN_WALLET_SIZE:
            return False, 100, None  # 100% confident it's NOT a wallet
            
        # Add confidence based on size
        if self.file_size >= self.TYPICAL_MIN_SIZE:
            self.confidence += 10
        if self.file_size >= 100 * 1024:  # 100KB+
            self.confidence += 5
            
        # Check Berkeley DB header
        if self._check_berkeley_db():
            self.confidence += 30
            wallet_info['db_type'] = 'Berkeley DB'
            wallet_info['db_version'] = self.db_version
        else:
            # Not Berkeley DB, much less likely to be a wallet
            self.confidence -= 20
            
        # Check for wallet-specific patterns
        pattern_count = self._check_wallet_patterns()
        if pattern_count > 0:
            # More patterns = higher confidence
            self.confidence += min(pattern_count * 10, 50)
            wallet_info['pattern_matches'] = pattern_count
            
        # Check file extension
        if file_path.lower().endswith('.dat'):
            self.confidence += 10
        elif 'wallet' in os.path.basename(file_path).lower():
            self.confidence += 15
            
        # Try to extract specific wallet info
        wallet_version = self._try_extract_version()
        if wallet_version:
            self.confidence += 10
            wallet_info['version'] = wallet_version
            
        # Check for encryption
        is_encrypted = self._check_encryption()
        wallet_info['encrypted'] = is_encrypted
        
        # Ensure confidence is within bounds
        self.confidence = max(0, min(100, self.confidence))
        
        # Decision threshold
        is_wallet = self.confidence >= 40
        
        return is_wallet, self.confidence, wallet_info
        
    def _check_berkeley_db(self) -> bool:
        """Check if file has Berkeley DB magic bytes"""
        try:
            with open(self.file_path, 'rb') as f:
                # Check first 12 bytes
                header = f.read(12)
                
                # Check for magic bytes
                for magic, version in self.BERKELEY_DB_MAGIC.items():
                    if magic in header:
                        self.is_berkeley_db = True
                        self.db_version = version
                        return True
                        
                # Also check at typical page boundaries
                for offset in [0, 512, 1024, 2048, 4096]:
                    f.seek(offset)
                    header = f.read(12)
                    for magic, version in self.BERKELEY_DB_MAGIC.items():
                        if magic in header:
                            self.is_berkeley_db = True
                            self.db_version = version
                            return True
                            
        except Exception:
            pass
            
        return False
        
    def _check_wallet_patterns(self) -> int:
        """Check for wallet-specific patterns in the file"""
        pattern_count = 0
        self.pattern_matches = []
        
        try:
            with open(self.file_path, 'rb') as f:
                # Read file in chunks to avoid memory issues
                chunk_size = 64 * 1024  # 64KB chunks
                
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                        
                    for pattern in self.WALLET_PATTERNS:
                        if pattern in chunk and pattern not in self.pattern_matches:
                            self.pattern_matches.append(pattern)
                            pattern_count += 1
                            
                    # Don't read entire huge files
                    if f.tell() > 10 * 1024 * 1024:  # 10MB
                        break
                        
        except Exception:
            pass
            
        return pattern_count
        
    def _try_extract_version(self) -> Optional[int]:
        """Try to extract wallet version"""
        try:
            with open(self.file_path, 'rb') as f:
                content = f.read(min(self.file_size, 1024 * 1024))  # Read up to 1MB
                
                # Look for version pattern
                version_idx = content.find(b'\x07version')
                if version_idx != -1 and version_idx + 20 < len(content):
                    # Try to parse version number (usually 4 bytes after key)
                    version_data = content[version_idx + 8:version_idx + 12]
                    if len(version_data) == 4:
                        version = struct.unpack('<I', version_data)[0]
                        if 10000 < version < 999999:  # Reasonable version range
                            return version
                            
        except Exception:
            pass
            
        return None
        
    def _check_encryption(self) -> bool:
        """Check if wallet appears to be encrypted"""
        try:
            with open(self.file_path, 'rb') as f:
                content = f.read(min(self.file_size, 1024 * 1024))
                
                # Look for master key pattern (indicates encryption)
                if b'mkey' in content or b'\x04mkey' in content:
                    return True
                    
        except Exception:
            pass
            
        return False
        
    def generate_report(self) -> str:
        """Generate a detailed analysis report"""
        report = []
        report.append(f"File: {self.file_path}")
        report.append(f"Size: {self.file_size:,} bytes")
        report.append(f"Berkeley DB: {'Yes - ' + self.db_version if self.is_berkeley_db else 'No'}")
        report.append(f"Pattern matches: {len(self.pattern_matches)}")
        if self.pattern_matches:
            report.append(f"Patterns found: {', '.join(p.decode('utf-8', errors='ignore') for p in self.pattern_matches[:5])}")
        report.append(f"Confidence: {self.confidence}%")
        
        return '\n'.join(report)


def scan_for_wallets(directory: str, recursive: bool = True) -> list:
    """
    Scan a directory for potential wallet files.
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        
    Returns:
        List of tuples: (file_path, is_wallet, confidence, info)
    """
    detector = WalletDetector()
    results = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Check .dat files and files with 'wallet' in name
                if file.endswith('.dat') or 'wallet' in file.lower():
                    file_path = os.path.join(root, file)
                    is_wallet, confidence, info = detector.analyze_file(file_path)
                    
                    if is_wallet or confidence > 20:  # Include maybes
                        results.append((file_path, is_wallet, confidence, info))
    else:
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                if file.endswith('.dat') or 'wallet' in file.lower():
                    file_path = os.path.join(directory, file)
                    is_wallet, confidence, info = detector.analyze_file(file_path)
                    
                    if is_wallet or confidence > 20:
                        results.append((file_path, is_wallet, confidence, info))
                        
    # Sort by confidence
    results.sort(key=lambda x: x[2], reverse=True)
    
    return results


def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) > 1:
        detector = WalletDetector()
        file_path = sys.argv[1]
        
        print("🔍 Analyzing file:", file_path)
        print("-" * 50)
        
        is_wallet, confidence, info = detector.analyze_file(file_path)
        
        print(detector.generate_report())
        print("-" * 50)
        
        if is_wallet:
            print(f"✅ This is likely a Bitcoin wallet! ({confidence}% confidence)")
        else:
            print(f"❌ This is probably NOT a Bitcoin wallet ({confidence}% confidence)")
            
        if info:
            print("\nAdditional info:")
            for key, value in info.items():
                print(f"  {key}: {value}")
    else:
        print("Usage: python3 wallet_detector.py <file>")

if __name__ == "__main__":
    main()