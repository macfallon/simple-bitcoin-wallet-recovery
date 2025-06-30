#!/usr/bin/env python3
import json
import requests
import time
from datetime import datetime

def check_blockstream_api(address):
    """Check balance using Blockstream API"""
    try:
        url = f"https://blockstream.info/api/address/{address}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            balance = (data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']) / 100000000
            return {
                'balance': balance,
                'tx_count': data['chain_stats']['tx_count'],
                'unconfirmed': data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
            }
    except:
        return None
    return None

def check_blockchain_info(address):
    """Check balance using blockchain.info API"""
    try:
        url = f"https://blockchain.info/balance?active={address}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            info = data.get(address, {})
            return {
                'balance': info.get('final_balance', 0) / 100000000,
                'tx_count': info.get('n_tx', 0)
            }
    except:
        return None
    return None

def check_blockcypher_api(address):
    """Check balance using BlockCypher API"""
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'balance': data.get('balance', 0) / 100000000,
                'unconfirmed': data.get('unconfirmed_balance', 0) / 100000000,
                'tx_count': data.get('n_tx', 0)
            }
    except:
        return None
    return None

def verify_address_balance(address):
    """Verify balance across multiple sources"""
    print(f"\nVerifying {address}...")
    
    results = {}
    
    # Check Blockstream
    print("  Checking Blockstream.info...", end='', flush=True)
    blockstream = check_blockstream_api(address)
    if blockstream:
        results['Blockstream'] = blockstream
        print(f" {blockstream['balance']:.8f} BTC")
    else:
        print(" Failed")
    time.sleep(0.5)
    
    # Check Blockchain.info
    print("  Checking Blockchain.info...", end='', flush=True)
    blockchain = check_blockchain_info(address)
    if blockchain:
        results['Blockchain.info'] = blockchain
        print(f" {blockchain['balance']:.8f} BTC")
    else:
        print(" Failed")
    time.sleep(0.5)
    
    # Check BlockCypher
    print("  Checking BlockCypher...", end='', flush=True)
    blockcypher = check_blockcypher_api(address)
    if blockcypher:
        results['BlockCypher'] = blockcypher
        print(f" {blockcypher['balance']:.8f} BTC")
    else:
        print(" Failed")
    
    return results

def main():
    print("=== BITCOIN BALANCE VERIFICATION ===")
    print(f"Verification time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Addresses with known balances
    addresses_to_check = [
        ("13cHqB1vTx94NNxom8NwHgFfn6E7bnmnTq", "Slush", 0.04179530),
        ("1Nf4xvHEBcxUoZXRp9Fi6QrUp1TCK7wcDk", "Eclipse", 0.04014620),
        ("19rNsCg6BgpuZWJTAWB9kkhrj8QqfycdpD", None, 0.02904965),
        ("19tpvtWxQ3cc7L3rWJqGiZbC9akEnLv2k7", None, 0.01019683),
        ("1F2fvzHoL9jCSRxz5W1oa3mZUeyQKLmQhT", None, 0.00026483)
    ]
    
    verified_total = 0
    all_results = []
    
    for address, label, expected_balance in addresses_to_check:
        label_str = f" ({label})" if label else ""
        print(f"\n{'='*60}")
        print(f"Address: {address}{label_str}")
        print(f"Expected balance: {expected_balance:.8f} BTC")
        
        results = verify_address_balance(address)
        
        # Analyze results
        balances = [r['balance'] for r in results.values() if 'balance' in r]
        if balances:
            avg_balance = sum(balances) / len(balances)
            verified_total += avg_balance
            
            print(f"\nVerified balance: {avg_balance:.8f} BTC")
            if len(set(balances)) == 1:
                print("✓ All sources agree on the balance")
            else:
                print("⚠ Sources report different balances:")
                for source, data in results.items():
                    print(f"  - {source}: {data['balance']:.8f} BTC")
            
            # Check for unconfirmed transactions
            unconfirmed = [r.get('unconfirmed', 0) for r in results.values()]
            if any(u > 0 for u in unconfirmed):
                print(f"⚠ Unconfirmed balance detected: {max(unconfirmed)/100000000:.8f} BTC")
            
            all_results.append({
                'address': address,
                'label': label,
                'balance': avg_balance,
                'verified': True
            })
        else:
            print("\n✗ Could not verify balance from any source")
            all_results.append({
                'address': address,
                'label': label,
                'balance': 0,
                'verified': False
            })
    
    print(f"\n{'='*60}")
    print("=== SUMMARY ===")
    print(f"Total verified balance: {verified_total:.8f} BTC")
    print(f"Successfully verified: {sum(1 for r in all_results if r['verified'])}/{len(all_results)} addresses")
    
    # Get current BTC price
    try:
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
        if response.status_code == 200:
            usd_rate = float(response.json()['data']['rates']['USD'])
            print(f"\nCurrent BTC price: ${usd_rate:,.2f} USD")
            print(f"Total value: ${verified_total * usd_rate:,.2f} USD")
    except:
        pass
    
    return all_results

if __name__ == "__main__":
    results = main()