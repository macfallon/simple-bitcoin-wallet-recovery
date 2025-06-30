#!/usr/bin/env python3
"""
Balance Checker Module
======================

Multi-source Bitcoin balance verification with retry logic and caching.
Checks balances across multiple blockchain APIs for reliability.
"""

import time
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

class BalanceChecker:
    """Check Bitcoin balances across multiple blockchain APIs"""
    
    # API endpoints
    APIS = {
        'blockchain_info': {
            'url': 'https://blockchain.info/balance?active={}',
            'batch_size': 100,
            'rate_limit': 1.0  # seconds between requests
        },
        'blockstream': {
            'url': 'https://blockstream.info/api/address/{}',
            'batch_size': 1,  # Single address only
            'rate_limit': 0.25
        },
        'blockcypher': {
            'url': 'https://api.blockcypher.com/v1/btc/main/addrs/{}/balance',
            'batch_size': 1,
            'rate_limit': 0.33
        },
        'mempool_space': {
            'url': 'https://mempool.space/api/address/{}',
            'batch_size': 1,
            'rate_limit': 0.1
        }
    }
    
    def __init__(self, cache_dir: str = '.balance_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Simple-Bitcoin-Wallet-Recovery/1.0'
        })
        self.stats = {
            'api_calls': 0,
            'cache_hits': 0,
            'errors': 0
        }
        
    def check_balance(self, address: str, use_cache: bool = True) -> Dict:
        """
        Check balance for a single address across multiple sources.
        
        Returns:
            Dict with balance, tx_count, and verification details
        """
        # Check cache first
        if use_cache:
            cached = self._get_cached_balance(address)
            if cached:
                self.stats['cache_hits'] += 1
                return cached
                
        results = {}
        
        # Try each API
        for api_name, api_config in self.APIS.items():
            try:
                balance_info = self._check_single_api(address, api_name, api_config)
                if balance_info:
                    results[api_name] = balance_info
                time.sleep(api_config['rate_limit'])
            except Exception as e:
                self.stats['errors'] += 1
                
        # Determine consensus
        if results:
            balance = self._get_consensus_balance(results)
            balance['sources'] = list(results.keys())
            balance['verified'] = len(results) >= 2
            
            # Cache the result
            if use_cache:
                self._cache_balance(address, balance)
                
            return balance
        else:
            return {
                'balance': 0,
                'tx_count': 0,
                'verified': False,
                'sources': [],
                'error': 'No API responded'
            }
            
    def check_batch(self, addresses: List[str], use_cache: bool = True) -> Dict[str, Dict]:
        """
        Check balances for multiple addresses efficiently.
        
        Returns:
            Dict mapping address to balance info
        """
        results = {}
        
        # First, check cache for all addresses
        uncached_addresses = []
        if use_cache:
            for address in addresses:
                cached = self._get_cached_balance(address)
                if cached:
                    results[address] = cached
                    self.stats['cache_hits'] += 1
                else:
                    uncached_addresses.append(address)
        else:
            uncached_addresses = addresses
            
        # Use blockchain.info for batch checking (most efficient)
        if uncached_addresses:
            batch_results = self._check_blockchain_info_batch(uncached_addresses)
            results.update(batch_results)
            
            # For addresses with balance, verify with another source
            for address, info in batch_results.items():
                if info.get('balance', 0) > 0:
                    # Verify with another API
                    verified = self._verify_balance(address, info['balance'])
                    info['verified'] = verified
                    
        return results
        
    def _check_single_api(self, address: str, api_name: str, api_config: Dict) -> Optional[Dict]:
        """Check balance using a specific API"""
        self.stats['api_calls'] += 1
        
        try:
            if api_name == 'blockchain_info':
                return self._parse_blockchain_info(address, api_config)
            elif api_name == 'blockstream':
                return self._parse_blockstream(address, api_config)
            elif api_name == 'blockcypher':
                return self._parse_blockcypher(address, api_config)
            elif api_name == 'mempool_space':
                return self._parse_mempool_space(address, api_config)
        except Exception:
            return None
            
    def _parse_blockchain_info(self, address: str, api_config: Dict) -> Optional[Dict]:
        """Parse blockchain.info API response"""
        url = api_config['url'].format(address)
        response = self.session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            addr_data = data.get(address, {})
            return {
                'balance': addr_data.get('final_balance', 0) / 100000000,
                'tx_count': addr_data.get('n_tx', 0),
                'total_received': addr_data.get('total_received', 0) / 100000000,
                'total_sent': addr_data.get('total_sent', 0) / 100000000
            }
        return None
        
    def _parse_blockstream(self, address: str, api_config: Dict) -> Optional[Dict]:
        """Parse Blockstream API response"""
        url = api_config['url'].format(address)
        response = self.session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            chain = data.get('chain_stats', {})
            mempool = data.get('mempool_stats', {})
            
            funded = chain.get('funded_txo_sum', 0)
            spent = chain.get('spent_txo_sum', 0)
            balance = (funded - spent) / 100000000
            
            # Add unconfirmed balance
            mempool_funded = mempool.get('funded_txo_sum', 0)
            mempool_spent = mempool.get('spent_txo_sum', 0)
            unconfirmed = (mempool_funded - mempool_spent) / 100000000
            
            return {
                'balance': balance,
                'unconfirmed_balance': unconfirmed,
                'tx_count': chain.get('tx_count', 0),
                'total_received': funded / 100000000,
                'total_sent': spent / 100000000
            }
        return None
        
    def _parse_blockcypher(self, address: str, api_config: Dict) -> Optional[Dict]:
        """Parse BlockCypher API response"""
        url = api_config['url'].format(address)
        response = self.session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'balance': data.get('balance', 0) / 100000000,
                'unconfirmed_balance': data.get('unconfirmed_balance', 0) / 100000000,
                'tx_count': data.get('n_tx', 0),
                'total_received': data.get('total_received', 0) / 100000000,
                'total_sent': data.get('total_sent', 0) / 100000000
            }
        return None
        
    def _parse_mempool_space(self, address: str, api_config: Dict) -> Optional[Dict]:
        """Parse mempool.space API response"""
        url = api_config['url'].format(address)
        response = self.session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            chain = data.get('chain_stats', {})
            mempool = data.get('mempool_stats', {})
            
            funded = chain.get('funded_txo_sum', 0)
            spent = chain.get('spent_txo_sum', 0)
            balance = (funded - spent) / 100000000
            
            return {
                'balance': balance,
                'tx_count': chain.get('tx_count', 0),
                'total_received': funded / 100000000,
                'total_sent': spent / 100000000
            }
        return None
        
    def _check_blockchain_info_batch(self, addresses: List[str]) -> Dict[str, Dict]:
        """Check multiple addresses using blockchain.info batch API"""
        results = {}
        api_config = self.APIS['blockchain_info']
        
        # Process in batches
        for i in range(0, len(addresses), api_config['batch_size']):
            batch = addresses[i:i + api_config['batch_size']]
            addr_param = '|'.join(batch)
            
            try:
                url = api_config['url'].format(addr_param)
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for address in batch:
                        addr_data = data.get(address, {})
                        balance = addr_data.get('final_balance', 0) / 100000000
                        
                        results[address] = {
                            'balance': balance,
                            'tx_count': addr_data.get('n_tx', 0),
                            'total_received': addr_data.get('total_received', 0) / 100000000,
                            'total_sent': addr_data.get('total_sent', 0) / 100000000,
                            'sources': ['blockchain_info'],
                            'verified': False
                        }
                        
                        # Cache if has balance
                        if balance > 0:
                            self._cache_balance(address, results[address])
                else:
                    # On error, add empty results
                    for address in batch:
                        results[address] = {
                            'balance': 0,
                            'tx_count': 0,
                            'sources': [],
                            'verified': False,
                            'error': f'HTTP {response.status_code}'
                        }
                        
            except Exception as e:
                # On error, add empty results
                for address in batch:
                    results[address] = {
                        'balance': 0,
                        'tx_count': 0,
                        'sources': [],
                        'verified': False,
                        'error': str(e)
                    }
                    
            # Rate limiting
            time.sleep(api_config['rate_limit'])
            
        return results
        
    def _verify_balance(self, address: str, expected_balance: float) -> bool:
        """Verify balance with another API source"""
        # Try blockstream for verification
        try:
            api_config = self.APIS['blockstream']
            result = self._parse_blockstream(address, api_config)
            
            if result:
                # Allow small difference due to unconfirmed transactions
                difference = abs(result['balance'] - expected_balance)
                return difference < 0.00000001  # 1 satoshi
        except:
            pass
            
        return False
        
    def _get_consensus_balance(self, results: Dict[str, Dict]) -> Dict:
        """Get consensus balance from multiple sources"""
        balances = [r['balance'] for r in results.values() if 'balance' in r]
        
        if not balances:
            return {'balance': 0, 'tx_count': 0}
            
        # Use median balance for consensus
        balances.sort()
        median_balance = balances[len(balances) // 2]
        
        # Get other stats from first complete result
        for result in results.values():
            if result.get('balance') == median_balance:
                return {
                    'balance': median_balance,
                    'tx_count': result.get('tx_count', 0),
                    'total_received': result.get('total_received', 0),
                    'total_sent': result.get('total_sent', 0)
                }
                
        # Fallback
        return {
            'balance': median_balance,
            'tx_count': max(r.get('tx_count', 0) for r in results.values())
        }
        
    def _get_cached_balance(self, address: str) -> Optional[Dict]:
        """Get balance from cache if fresh"""
        cache_file = self.cache_dir / f"{address}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    
                # Check if cache is fresh (less than 1 hour old)
                cached_time = datetime.fromisoformat(data['cached_at'])
                if datetime.now() - cached_time < timedelta(hours=1):
                    return data['balance_info']
            except:
                pass
                
        return None
        
    def _cache_balance(self, address: str, balance_info: Dict):
        """Cache balance information"""
        cache_file = self.cache_dir / f"{address}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'address': address,
                    'balance_info': balance_info,
                    'cached_at': datetime.now().isoformat()
                }, f)
        except:
            pass
            
    def get_stats(self) -> Dict:
        """Get checker statistics"""
        return self.stats.copy()
        
    def clear_cache(self):
        """Clear all cached balances"""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()


# Convenience functions
def check_balance(address: str) -> Dict:
    """Quick balance check for a single address"""
    checker = BalanceChecker()
    return checker.check_balance(address)
    
def check_addresses(addresses: List[str]) -> Dict[str, Dict]:
    """Quick balance check for multiple addresses"""
    checker = BalanceChecker()
    return checker.check_batch(addresses)


if __name__ == "__main__":
    # Test the balance checker
    test_addresses = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block
        "13cHqB1vTx94NNxom8NwHgFfn6E7bnmnTq",  # From our recovery
        "1BitcoinEaterAddressDontSendf59kuE"   # Burn address
    ]
    
    print("🔍 Testing Balance Checker")
    print("-" * 50)
    
    checker = BalanceChecker()
    
    for address in test_addresses:
        print(f"\nChecking {address}...")
        result = checker.check_balance(address)
        
        if result.get('balance', 0) > 0:
            print(f"  ✅ Balance: {result['balance']:.8f} BTC")
            print(f"  📊 Transactions: {result.get('tx_count', 0)}")
            print(f"  ✓ Verified: {result.get('verified', False)}")
            print(f"  📡 Sources: {', '.join(result.get('sources', []))}")
        else:
            print(f"  ❌ No balance")
            
    print(f"\n📊 Stats: {checker.get_stats()}")