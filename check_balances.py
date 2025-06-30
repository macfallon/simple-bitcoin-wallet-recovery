#!/usr/bin/env python3
import json
import requests
import time

def check_balance_blockchain_info(addresses):
    """Check balances using blockchain.info API (max 100 addresses at a time)"""
    results = []
    
    # Process in batches of 100
    for i in range(0, len(addresses), 100):
        batch = addresses[i:i+100]
        addr_string = '|'.join(batch)
        
        try:
            url = f"https://blockchain.info/balance?active={addr_string}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for addr, info in data.items():
                    balance = info['final_balance'] / 100000000  # Convert satoshis to BTC
                    if balance > 0:
                        results.append({
                            'address': addr,
                            'balance': balance,
                            'n_tx': info['n_tx']
                        })
            else:
                print(f"Error checking batch {i//100 + 1}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error checking batch {i//100 + 1}: {e}")
            
        # Rate limiting
        if i + 100 < len(addresses):
            time.sleep(1)
    
    return results

def main():
    # Load addresses
    print("Loading wallet addresses...")
    with open('wallet_addresses.txt', 'r') as f:
        addresses = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(addresses)} addresses in wallet")
    print()
    
    # Check labeled addresses first
    with open('wallet_clean.json', 'r') as f:
        wallet_data = json.load(f)
    
    labeled = [(k['addr'], k.get('label', '')) for k in wallet_data['keys'] if 'label' in k]
    
    if labeled:
        print("Checking labeled addresses first...")
        labeled_addrs = [addr for addr, label in labeled]
        labeled_results = check_balance_blockchain_info(labeled_addrs)
        
        print("\n=== Labeled Addresses ===")
        for addr, label in labeled:
            balance_info = next((r for r in labeled_results if r['address'] == addr), None)
            if balance_info:
                print(f"{addr} ({label}): {balance_info['balance']:.8f} BTC ({balance_info['n_tx']} transactions)")
            else:
                print(f"{addr} ({label}): 0 BTC")
    
    # Check all addresses
    print("\nChecking all addresses (this may take a while)...")
    all_results = check_balance_blockchain_info(addresses)
    
    # Summary
    print("\n=== WALLET BALANCE SUMMARY ===")
    if all_results:
        total_balance = sum(r['balance'] for r in all_results)
        print(f"Addresses with balance: {len(all_results)}")
        print(f"Total balance: {total_balance:.8f} BTC")
        print(f"\nAddresses with balance:")
        for result in sorted(all_results, key=lambda x: x['balance'], reverse=True)[:20]:
            print(f"  {result['address']}: {result['balance']:.8f} BTC")
        
        if len(all_results) > 20:
            print(f"  ... and {len(all_results) - 20} more addresses with balance")
    else:
        print("No addresses with balance found.")
        print("The wallet appears to be empty.")

if __name__ == "__main__":
    main()