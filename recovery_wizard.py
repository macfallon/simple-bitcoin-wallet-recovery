#!/usr/bin/env python3
"""
Simple Bitcoin Wallet Recovery Wizard
=====================================

A user-friendly tool to recover Bitcoin from old wallet.dat files.
This tool helped recover $13,062 from a forgotten wallet!

Usage:
    python3 recovery_wizard.py --scandir /path/to/scan
    python3 recovery_wizard.py wallet.dat
"""

import os
import sys
import json
import time
import shutil
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Add lib to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Version info
VERSION = "2.0.0"
SUCCESS_STORY = """
This tool was born from a real success story: In December 2024, using these
techniques, we recovered 0.12145281 BTC from an old wallet.dat file
found on a backup drive. Now you can do the same!
"""

class WalletRecoveryWizard:
    """Main orchestrator for the wallet recovery process"""
    
    def __init__(self):
        self.start_time = time.time()
        self.work_dir = None
        self.scratch_dir = None
        self.output_dir = None
        self.found_wallets = []
        self.funded_wallets = []
        self.total_btc_found = 0
        self.files_scanned = 0
        self.dat_files_found = 0
        self.errors = []
        
    def print_banner(self):
        """Display welcome banner"""
        print("="*70)
        print("🔑 Simple Bitcoin Wallet Recovery Wizard v" + VERSION)
        print("="*70)
        print(SUCCESS_STORY)
        print("="*70)
        print()
        
    def setup_work_directories(self):
        """Create organized work directory structure"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.work_dir = Path(f"bitcoin_recovery_{timestamp}")
        self.scratch_dir = self.work_dir / "scratch"
        self.output_dir = self.work_dir / "output"
        
        # Create directories
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "funded_wallets").mkdir(exist_ok=True)
        (self.output_dir / "empty_wallets").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        # Create README
        readme_path = self.work_dir / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(f"""Bitcoin Wallet Recovery Results
===============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Directory Structure:
- scratch/          : Temporary work files (can be deleted)
- output/          : Your results
  - summary_report.txt    : Overview of all findings
  - funded_wallets/      : Wallets with Bitcoin found
  - empty_wallets/       : Wallets with no balance
  - logs/               : Detailed scan logs

Next Steps:
1. Check summary_report.txt for overview
2. Look in funded_wallets/ for any Bitcoin found
3. Follow the transfer guide for each funded wallet

Security Reminder:
- Keep private keys secure
- Delete files after transferring Bitcoin
- Never share private keys online
""")
        
        print(f"📁 Created work directory: {self.work_dir}/")
        print()
        
    def scan_directory(self, directory: Path, dry_run: bool = False) -> List[Path]:
        """Scan directory recursively for .dat files"""
        print(f"🔍 Scanning {directory} for potential wallet files...")
        if dry_run:
            print("(DRY RUN - No actual processing will occur)")
        print()
        
        dat_files = []
        total_files = 0
        
        # First, count total files for progress
        print("Counting files...")
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            total_files += len(files)
            
        print(f"Total files to scan: {total_files:,}")
        print()
        
        # Now scan with progress
        start_time = time.time()
        last_update = start_time
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and our work directory
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != str(self.work_dir)]
            
            for file in files:
                self.files_scanned += 1
                
                # Update progress every second
                if time.time() - last_update > 1:
                    self._show_progress(self.files_scanned, total_files, len(dat_files))
                    last_update = time.time()
                
                # Check for .dat files
                if file.lower().endswith('.dat'):
                    file_path = Path(root) / file
                    
                    # Skip tiny files (likely not wallets)
                    try:
                        if file_path.stat().st_size < 10 * 1024:  # 10KB minimum
                            continue
                    except:
                        continue
                        
                    dat_files.append(file_path)
                    self.dat_files_found += 1
                    
        # Final progress update
        self._show_progress(self.files_scanned, total_files, len(dat_files), final=True)
        
        print(f"\n✅ Scan complete!")
        print(f"   Files scanned: {self.files_scanned:,}")
        print(f"   .dat files found: {len(dat_files)}")
        print(f"   Time taken: {time.time() - start_time:.1f} seconds")
        print()
        
        return dat_files
        
    def _show_progress(self, current: int, total: int, found: int, final: bool = False):
        """Display progress bar"""
        if total == 0:
            return
            
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        status = f"Found: {found} .dat files"
        if not final:
            print(f"\rProgress: [{bar}] {percent:.1f}% ({current:,}/{total:,}) {status}", end='', flush=True)
        else:
            print(f"\rProgress: [{bar}] {percent:.1f}% ({current:,}/{total:,}) {status}")
            
    def analyze_dat_files(self, dat_files: List[Path]) -> None:
        """Analyze each .dat file to check if it's a Bitcoin wallet"""
        print(f"🔎 Analyzing {len(dat_files)} .dat files...")
        print()
        
        from lib.wallet_detector import WalletDetector
        detector = WalletDetector()
        
        for i, dat_file in enumerate(dat_files):
            print(f"[{i+1}/{len(dat_files)}] Checking: {dat_file}")
            
            try:
                # Quick detection
                is_wallet, confidence, info = detector.analyze_file(str(dat_file))
                
                if is_wallet or confidence > 30:  # Include maybes
                    wallet_info = {
                        'path': dat_file,
                        'confidence': confidence,
                        'info': info,
                        'hash': self._get_file_hash(dat_file)
                    }
                    
                    if is_wallet:
                        print(f"  ✅ Bitcoin wallet detected! (Confidence: {confidence}%)")
                        self.found_wallets.append(wallet_info)
                    else:
                        print(f"  🤔 Possible wallet (Confidence: {confidence}%)")
                        self.found_wallets.append(wallet_info)
                else:
                    print(f"  ❌ Not a Bitcoin wallet")
                    
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
                self.errors.append({'file': str(dat_file), 'error': str(e)})
                
        print(f"\n📊 Analysis complete: {len(self.found_wallets)} potential wallets found")
        
    def process_wallets(self) -> None:
        """Process each found wallet to extract keys and check balances"""
        if not self.found_wallets:
            print("\n😔 No Bitcoin wallets found in scan")
            return
            
        print(f"\n💰 Processing {len(self.found_wallets)} wallet(s)...")
        print()
        
        for i, wallet_info in enumerate(self.found_wallets):
            wallet_path = wallet_info['path']
            print(f"\n{'='*60}")
            print(f"[{i+1}/{len(self.found_wallets)}] Processing: {wallet_path}")
            print(f"Confidence: {wallet_info['confidence']}%")
            
            # Create scratch directory for this wallet
            wallet_id = f"wallet_{i+1:03d}_{wallet_path.stem}"
            wallet_scratch = self.scratch_dir / wallet_id
            wallet_scratch.mkdir(exist_ok=True)
            
            try:
                # Extract wallet data
                success, wallet_data = self._extract_wallet_data(wallet_path, wallet_scratch)
                if not success:
                    continue
                    
                # Check balances
                funded_addresses = self._check_wallet_balances(wallet_data, wallet_scratch)
                
                # Save results
                if funded_addresses:
                    self.funded_wallets.append({
                        'wallet_info': wallet_info,
                        'wallet_data': wallet_data,
                        'funded_addresses': funded_addresses,
                        'total_btc': sum(a['balance'] for a in funded_addresses)
                    })
                    self.total_btc_found += sum(a['balance'] for a in funded_addresses)
                    
                    # Export to funded directory
                    self._export_funded_wallet(wallet_id, wallet_info, funded_addresses)
                else:
                    # Save to empty wallets
                    self._export_empty_wallet(wallet_id, wallet_info, wallet_data)
                    
            except Exception as e:
                print(f"  ❌ Error processing wallet: {e}")
                self.errors.append({'wallet': str(wallet_path), 'error': str(e)})
                
    def _extract_wallet_data(self, wallet_path: Path, scratch_dir: Path) -> Tuple[bool, Optional[Dict]]:
        """Extract data from wallet using pywallet"""
        print("  📤 Extracting wallet data...")
        
        try:
            import subprocess
            
            # Run pywallet
            dump_file = scratch_dir / "wallet_dump.json"
            cmd = [
                sys.executable, 'pywallet.py',
                f'--wallet={wallet_path}',
                '--dumpwallet'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ Failed to extract wallet data")
                with open(scratch_dir / "error.log", 'w') as f:
                    f.write(result.stderr)
                return False, None
                
            # Parse JSON from output
            lines = result.stdout.split('\n')
            json_lines = []
            json_started = False
            
            for line in lines:
                if line.strip().startswith('{'):
                    json_started = True
                if json_started and line.strip():
                    json_lines.append(line)
                    
            if not json_lines:
                print(f"  ❌ No valid wallet data found")
                return False, None
                
            wallet_json = '\n'.join(json_lines)
            wallet_data = json.loads(wallet_json)
            
            # Save clean dump
            with open(dump_file, 'w') as f:
                json.dump(wallet_data, f, indent=2)
                
            addresses = wallet_data.get('keys', [])
            print(f"  ✅ Extracted {len(addresses)} addresses")
            
            return True, wallet_data
            
        except Exception as e:
            print(f"  ❌ Extraction error: {e}")
            return False, None
            
    def _check_wallet_balances(self, wallet_data: Dict, scratch_dir: Path) -> List[Dict]:
        """Check balances for wallet addresses"""
        addresses = wallet_data.get('keys', [])
        if not addresses:
            return []
            
        print(f"  💸 Checking balances for {len(addresses)} addresses...")
        
        try:
            from lib.balance_checker import BalanceChecker
            checker = BalanceChecker(cache_dir=str(scratch_dir / '.cache'))
            
            # Extract just addresses
            addr_list = [key['addr'] for key in addresses[:1000]]  # Limit to first 1000
            
            # Check in batches
            results = checker.check_batch(addr_list)
            
            # Find funded addresses
            funded = []
            for key in addresses:
                addr = key['addr']
                if addr in results and results[addr].get('balance', 0) > 0:
                    funded.append({
                        'address': addr,
                        'balance': results[addr]['balance'],
                        'private_key': key.get('sec', ''),
                        'compressed': key.get('compressed', False),
                        'tx_count': results[addr].get('tx_count', 0)
                    })
                    
            if funded:
                total_btc = sum(a['balance'] for a in funded)
                print(f"  💎 Found {len(funded)} funded addresses!")
                print(f"  💰 Total: {total_btc:.8f} BTC")
            else:
                print(f"  😔 No funds found")
                
            return funded
            
        except Exception as e:
            print(f"  ⚠️  Balance check error: {e}")
            return []
            
    def _export_funded_wallet(self, wallet_id: str, wallet_info: Dict, funded_addresses: List[Dict]) -> None:
        """Export funded wallet information"""
        output_dir = self.output_dir / "funded_wallets" / wallet_id
        output_dir.mkdir(exist_ok=True)
        
        # Save private keys
        with open(output_dir / "private_keys.txt", 'w') as f:
            f.write(f"# Bitcoin Private Keys - KEEP SECURE!\n")
            f.write(f"# Wallet: {wallet_info['path']}\n")
            f.write(f"# Total Balance: {sum(a['balance'] for a in funded_addresses):.8f} BTC\n")
            f.write("#" + "="*60 + "\n\n")
            
            for addr in funded_addresses:
                f.write(f"# Address: {addr['address']}\n")
                f.write(f"# Balance: {addr['balance']:.8f} BTC\n")
                f.write(f"{addr['private_key']}\n\n")
                
        # Save detailed info
        with open(output_dir / "wallet_info.json", 'w') as f:
            json.dump({
                'wallet_path': str(wallet_info['path']),
                'confidence': wallet_info['confidence'],
                'total_btc': sum(a['balance'] for a in funded_addresses),
                'addresses': funded_addresses
            }, f, indent=2)
            
        # Create transfer guide
        self._create_transfer_guide(output_dir, funded_addresses)
        
    def _export_empty_wallet(self, wallet_id: str, wallet_info: Dict, wallet_data: Dict) -> None:
        """Export empty wallet information"""
        output_file = self.output_dir / "empty_wallets" / f"{wallet_id}_info.txt"
        
        with open(output_file, 'w') as f:
            f.write(f"Empty Wallet Summary\n")
            f.write("="*50 + "\n")
            f.write(f"Path: {wallet_info['path']}\n")
            f.write(f"Confidence: {wallet_info['confidence']}%\n")
            f.write(f"Total addresses: {len(wallet_data.get('keys', []))}\n")
            f.write(f"Status: No Bitcoin found\n")
            
    def _create_transfer_guide(self, output_dir: Path, funded_addresses: List[Dict]) -> None:
        """Create a transfer guide for funded wallet"""
        total_btc = sum(a['balance'] for a in funded_addresses)
        
        with open(output_dir / "TRANSFER_GUIDE.txt", 'w') as f:
            f.write(f"""Bitcoin Transfer Guide
======================

Total Balance: {total_btc:.8f} BTC

Quick Steps:
1. Install Electrum from https://electrum.org
2. Create new wallet → "Import Bitcoin addresses or private keys"
3. Copy contents of private_keys.txt
4. Send to your exchange or hardware wallet

Security:
- Send a test transaction first (0.001 BTC)
- Delete these files after successful transfer
- Never share private keys online

For detailed instructions, see the main transfer guide.
""")
            
    def generate_final_report(self) -> None:
        """Generate comprehensive final report"""
        report_path = self.output_dir / "summary_report.txt"
        
        elapsed_time = time.time() - self.start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        with open(report_path, 'w') as f:
            f.write("Bitcoin Wallet Recovery Scan Report\n")
            f.write("="*60 + "\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Time Elapsed: {int(hours)}h {int(minutes)}m {int(seconds)}s\n")
            f.write("\n")
            
            f.write("Summary:\n")
            f.write(f"- Files scanned: {self.files_scanned:,}\n")
            f.write(f"- .dat files found: {self.dat_files_found}\n")
            f.write(f"- Potential wallets: {len(self.found_wallets)}\n")
            f.write(f"- Wallets with balance: {len(self.funded_wallets)}\n")
            f.write(f"- Total Bitcoin found: {self.total_btc_found:.8f} BTC\n")
            
            # Add USD value
            try:
                import requests
                response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
                if response.status_code == 200:
                    usd_rate = float(response.json()['data']['rates']['USD'])
                    f.write(f"- Estimated USD value: ${self.total_btc_found * usd_rate:,.2f}\n")
            except:
                pass
                
            f.write("\n")
            
            if self.funded_wallets:
                f.write("Funded Wallets:\n")
                f.write("-"*60 + "\n")
                for i, wallet in enumerate(self.funded_wallets):
                    f.write(f"\n{i+1}. {wallet['wallet_info']['path']}\n")
                    f.write(f"   Balance: {wallet['total_btc']:.8f} BTC\n")
                    f.write(f"   Addresses with funds: {len(wallet['funded_addresses'])}\n")
                    f.write(f"   Confidence: {wallet['wallet_info']['confidence']}%\n")
                    
            if self.errors:
                f.write("\n\nErrors Encountered:\n")
                f.write("-"*60 + "\n")
                for error in self.errors[:10]:  # First 10 errors
                    f.write(f"- {error}\n")
                    
        # Also save detailed log
        log_path = self.output_dir / "logs" / "scan_log.json"
        with open(log_path, 'w') as f:
            json.dump({
                'scan_time': datetime.now().isoformat(),
                'stats': {
                    'files_scanned': self.files_scanned,
                    'dat_files_found': self.dat_files_found,
                    'wallets_found': len(self.found_wallets),
                    'funded_wallets': len(self.funded_wallets),
                    'total_btc': self.total_btc_found
                },
                'wallets': self.found_wallets,
                'errors': self.errors
            }, f, indent=2)
            
        print(f"\n📄 Final report saved to: {report_path}")
        
    def _get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file (first 1MB)"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read first 1MB
                data = f.read(1024 * 1024)
                sha256_hash.update(data)
            return sha256_hash.hexdigest()[:16]  # First 16 chars
        except:
            return "unknown"
            
    def cleanup_scratch(self, force: bool = False) -> None:
        """Clean up scratch directory"""
        if not force:
            response = input("\nDelete scratch directory? (y/N): ")
            if response.lower() != 'y':
                return
                
        try:
            shutil.rmtree(self.scratch_dir)
            print("✅ Scratch directory cleaned up")
        except Exception as e:
            print(f"⚠️  Could not clean scratch: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Simple Bitcoin Wallet Recovery - Recover Bitcoin from old wallet files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=SUCCESS_STORY
    )
    
    # Main options
    parser.add_argument('wallet', nargs='?', help='Single wallet.dat file to analyze')
    parser.add_argument('--scandir', metavar='DIR', help='Scan directory recursively for wallet files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be scanned without processing')
    parser.add_argument('--quiet', action='store_true', help='Minimal output, just write results')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    # Create wizard instance
    wizard = WalletRecoveryWizard()
    
    if not args.quiet:
        wizard.print_banner()
        
    # Setup work directories
    wizard.setup_work_directories()
    
    try:
        if args.scandir:
            # Directory scan mode
            scan_path = Path(args.scandir)
            if not scan_path.exists():
                print(f"❌ Error: Directory '{scan_path}' does not exist")
                sys.exit(1)
                
            # Scan for .dat files
            dat_files = wizard.scan_directory(scan_path, dry_run=args.dry_run)
            
            if not args.dry_run and dat_files:
                # Analyze found files
                wizard.analyze_dat_files(dat_files)
                
                # Process wallets
                wizard.process_wallets()
                
        elif args.wallet:
            # Single wallet mode
            wallet_path = Path(args.wallet)
            if not wallet_path.exists():
                print(f"❌ Error: File '{wallet_path}' does not exist")
                sys.exit(1)
                
            # Process single wallet
            wizard.analyze_dat_files([wallet_path])
            wizard.process_wallets()
            
        else:
            # Interactive mode
            print("Choose an option:")
            print("1. Scan a directory for wallets")
            print("2. Analyze a specific wallet file")
            choice = input("\nEnter choice (1 or 2): ").strip()
            
            if choice == '1':
                path = input("Enter directory path to scan: ").strip()
                scan_path = Path(path)
                if scan_path.exists():
                    dat_files = wizard.scan_directory(scan_path)
                    if dat_files:
                        wizard.analyze_dat_files(dat_files)
                        wizard.process_wallets()
                else:
                    print(f"❌ Error: Directory '{scan_path}' does not exist")
                    
            elif choice == '2':
                path = input("Enter wallet file path: ").strip()
                wallet_path = Path(path)
                if wallet_path.exists():
                    wizard.analyze_dat_files([wallet_path])
                    wizard.process_wallets()
                else:
                    print(f"❌ Error: File '{wallet_path}' does not exist")
                    
    finally:
        # Generate final report
        wizard.generate_final_report()
        
        # Summary
        print("\n" + "="*60)
        print("🏁 Recovery Complete!")
        print("="*60)
        
        if wizard.total_btc_found > 0:
            print(f"🎉 SUCCESS! Found {wizard.total_btc_found:.8f} BTC!")
            print(f"📁 Check {wizard.output_dir}/funded_wallets/ for private keys")
            print(f"📄 See {wizard.output_dir}/summary_report.txt for details")
        else:
            print("😔 No Bitcoin found in scanned wallets")
            print(f"📄 See {wizard.output_dir}/summary_report.txt for details")
            
        print(f"\n📂 All results saved to: {wizard.work_dir}/")
        
        # Offer to clean up
        if not args.quiet:
            wizard.cleanup_scratch()
            
        print("\n✨ Thank you for using Simple Bitcoin Wallet Recovery!")
        print("🔒 Remember to securely delete private keys after use")

if __name__ == "__main__":
    main()