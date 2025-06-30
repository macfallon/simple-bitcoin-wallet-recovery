#!/usr/bin/env python3
"""
Wallet History Analyzer
======================

Analyzes the complete blockchain history of a wallet to assess privacy risks
before making it public as an example.
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path

class WalletHistoryAnalyzer:
    """Analyze wallet transaction history and privacy risks"""
    
    def __init__(self):
        self.addresses = []
        self.transactions = []
        self.max_balance = 0
        self.first_seen = None
        self.last_seen = None
        self.privacy_score = 100  # Start at 100, deduct for risks
        
    def extract_addresses(self, wallet_path: str) -> List[str]:
        """Extract all addresses from wallet file"""
        print(f"📤 Extracting addresses from {wallet_path}...")
        
        try:
            # Run pywallet to dump wallet
            cmd = [
                sys.executable, 'pywallet.py',
                f'--wallet={wallet_path}',
                '--dumpwallet'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.DEVNULL)
            
            if result.returncode != 0:
                print("❌ Failed to extract wallet data")
                return []
                
            # Parse JSON from output
            lines = result.stdout.split('\n')
            json_lines = []
            json_started = False
            
            for line in lines:
                if line.strip().startswith('{'):
                    json_started = True
                if json_started and line.strip():
                    json_lines.append(line)
                    
            wallet_json = '\n'.join(json_lines)
            wallet_data = json.loads(wallet_json)
            
            # Extract addresses
            addresses = []
            for key in wallet_data.get('keys', []):
                addresses.append(key['addr'])
                
            self.addresses = addresses
            print(f"✅ Found {len(addresses)} addresses")
            return addresses
            
        except Exception as e:
            print(f"❌ Error extracting addresses: {e}")
            return []
            
    def analyze_address_history(self, address: str) -> Dict:
        """Get complete transaction history for an address"""
        try:
            # Use blockchain.info API
            url = f"https://blockchain.info/rawaddr/{address}?limit=1000"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Calculate max balance (in satoshis)
                max_balance = 0
                current_balance = 0
                
                # Sort transactions by time
                txs = sorted(data.get('txs', []), key=lambda x: x.get('time', 0))
                
                for tx in txs:
                    # Calculate balance change
                    received = sum(out['value'] for out in tx.get('out', []) 
                                 if out.get('addr') == address)
                    sent = sum(inp.get('prev_out', {}).get('value', 0) 
                             for inp in tx.get('inputs', [])
                             if inp.get('prev_out', {}).get('addr') == address)
                    
                    current_balance += received - sent
                    max_balance = max(max_balance, current_balance)
                    
                return {
                    'address': address,
                    'n_tx': data.get('n_tx', 0),
                    'total_received': data.get('total_received', 0),
                    'total_sent': data.get('total_sent', 0),
                    'final_balance': data.get('final_balance', 0),
                    'max_balance': max_balance,
                    'first_tx_time': txs[0].get('time') if txs else None,
                    'last_tx_time': txs[-1].get('time') if txs else None,
                    'transactions': len(txs)
                }
            else:
                return None
                
        except Exception as e:
            print(f"  Error analyzing {address}: {e}")
            return None
            
    def analyze_wallet_history(self, addresses: List[str]) -> Dict:
        """Analyze complete wallet history"""
        print(f"\n🔍 Analyzing transaction history for {len(addresses)} addresses...")
        print("This may take a few minutes...\n")
        
        results = {
            'addresses_with_history': 0,
            'total_transactions': 0,
            'max_balance_satoshis': 0,
            'max_balance_btc': 0,
            'total_received_satoshis': 0,
            'total_sent_satoshis': 0,
            'first_seen': None,
            'last_seen': None,
            'address_details': []
        }
        
        for i, address in enumerate(addresses):
            print(f"[{i+1}/{len(addresses)}] Checking {address}...", end='', flush=True)
            
            history = self.analyze_address_history(address)
            
            if history and history['n_tx'] > 0:
                print(f" {history['n_tx']} transactions")
                
                results['addresses_with_history'] += 1
                results['total_transactions'] += history['n_tx']
                results['max_balance_satoshis'] = max(
                    results['max_balance_satoshis'], 
                    history['max_balance']
                )
                results['total_received_satoshis'] += history['total_received']
                results['total_sent_satoshis'] += history['total_sent']
                
                # Track time range
                if history['first_tx_time']:
                    if not results['first_seen'] or history['first_tx_time'] < results['first_seen']:
                        results['first_seen'] = history['first_tx_time']
                        
                if history['last_tx_time']:
                    if not results['last_seen'] or history['last_tx_time'] > results['last_seen']:
                        results['last_seen'] = history['last_tx_time']
                        
                results['address_details'].append(history)
            else:
                print(" no history")
                
        # Convert to BTC
        results['max_balance_btc'] = results['max_balance_satoshis'] / 100000000
        results['total_received_btc'] = results['total_received_satoshis'] / 100000000
        results['total_sent_btc'] = results['total_sent_satoshis'] / 100000000
        
        return results
        
    def assess_privacy_risks(self, analysis: Dict) -> Tuple[int, List[str]]:
        """Assess privacy risks and return score (0-100) and warnings"""
        score = 100
        warnings = []
        
        # Check max balance
        if analysis['max_balance_btc'] > 10:
            score -= 40
            warnings.append(f"⚠️  HIGH RISK: Wallet held {analysis['max_balance_btc']:.2f} BTC")
        elif analysis['max_balance_btc'] > 1:
            score -= 25
            warnings.append(f"⚠️  MEDIUM RISK: Wallet held {analysis['max_balance_btc']:.2f} BTC")
        elif analysis['max_balance_btc'] > 0.1:
            score -= 10
            warnings.append(f"ℹ️  Low risk: Wallet held {analysis['max_balance_btc']:.2f} BTC")
            
        # Check recency
        if analysis['last_seen']:
            last_date = datetime.fromtimestamp(analysis['last_seen'])
            days_ago = (datetime.now() - last_date).days
            
            if days_ago < 365:
                score -= 30
                warnings.append(f"⚠️  HIGH RISK: Last activity {days_ago} days ago")
            elif days_ago < 730:
                score -= 15
                warnings.append(f"⚠️  MEDIUM RISK: Last activity {days_ago} days ago")
            else:
                warnings.append(f"✅ Low risk: Last activity {days_ago} days ago")
                
        # Check transaction count
        if analysis['total_transactions'] > 100:
            score -= 20
            warnings.append(f"⚠️  HIGH RISK: {analysis['total_transactions']} transactions (extensive history)")
        elif analysis['total_transactions'] > 20:
            score -= 10
            warnings.append(f"ℹ️  Medium activity: {analysis['total_transactions']} transactions")
            
        # Check address usage
        if analysis['addresses_with_history'] > 10:
            score -= 15
            warnings.append(f"⚠️  Multiple addresses used: {analysis['addresses_with_history']}")
            
        return max(0, score), warnings
        
    def generate_report(self, wallet_path: str, analysis: Dict, privacy_score: int, warnings: List[str]):
        """Generate privacy analysis report"""
        report = []
        report.append("="*70)
        report.append("WALLET PRIVACY ANALYSIS REPORT")
        report.append("="*70)
        report.append(f"Wallet: {wallet_path}")
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("SUMMARY")
        report.append("-"*40)
        report.append(f"Total Addresses: {len(self.addresses)}")
        report.append(f"Addresses with History: {analysis['addresses_with_history']}")
        report.append(f"Total Transactions: {analysis['total_transactions']}")
        report.append("")
        
        report.append("BALANCE HISTORY")
        report.append("-"*40)
        report.append(f"Maximum Balance: {analysis['max_balance_btc']:.8f} BTC")
        report.append(f"Total Received: {analysis['total_received_btc']:.8f} BTC")
        report.append(f"Total Sent: {analysis['total_sent_btc']:.8f} BTC")
        report.append("")
        
        report.append("TIME RANGE")
        report.append("-"*40)
        if analysis['first_seen']:
            first_date = datetime.fromtimestamp(analysis['first_seen'])
            last_date = datetime.fromtimestamp(analysis['last_seen'])
            report.append(f"First Activity: {first_date.strftime('%Y-%m-%d')}")
            report.append(f"Last Activity: {last_date.strftime('%Y-%m-%d')}")
            report.append(f"Days Since Last Use: {(datetime.now() - last_date).days}")
        else:
            report.append("No transaction history found")
        report.append("")
        
        report.append("PRIVACY ASSESSMENT")
        report.append("-"*40)
        report.append(f"Privacy Score: {privacy_score}/100")
        
        if privacy_score >= 80:
            report.append("✅ LOW RISK - Generally safe to use as example")
        elif privacy_score >= 50:
            report.append("⚠️  MEDIUM RISK - Consider creating fresh wallet")
        else:
            report.append("🛑 HIGH RISK - Do not use as public example")
            
        report.append("")
        report.append("Warnings:")
        for warning in warnings:
            report.append(f"  {warning}")
            
        report.append("")
        report.append("RECOMMENDATION")
        report.append("-"*40)
        
        if privacy_score >= 80:
            report.append("This wallet can be used as a public example with proper warnings.")
            report.append("Add clear notices that it's for demonstration only.")
        elif privacy_score >= 50:
            report.append("Consider creating a fresh test wallet instead.")
            report.append("The transaction history poses moderate privacy risks.")
        else:
            report.append("DO NOT use this wallet as a public example.")
            report.append("Create a fresh test wallet or use testnet instead.")
            
        return "\n".join(report)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 wallet_history_analyzer.py <wallet.dat>")
        sys.exit(1)
        
    wallet_path = sys.argv[1]
    
    if not os.path.exists(wallet_path):
        print(f"Error: {wallet_path} not found")
        sys.exit(1)
        
    analyzer = WalletHistoryAnalyzer()
    
    # Extract addresses
    addresses = analyzer.extract_addresses(wallet_path)
    
    if not addresses:
        print("No addresses found in wallet")
        sys.exit(1)
        
    # Analyze history
    analysis = analyzer.analyze_wallet_history(addresses)
    
    # Assess privacy
    privacy_score, warnings = analyzer.assess_privacy_risks(analysis)
    
    # Generate report
    report = analyzer.generate_report(wallet_path, analysis, privacy_score, warnings)
    
    print("\n" + report)
    
    # Save report
    report_path = Path(wallet_path).stem + "_privacy_analysis.txt"
    with open(report_path, 'w') as f:
        f.write(report)
        
    print(f"\n📄 Report saved to: {report_path}")

if __name__ == "__main__":
    main()