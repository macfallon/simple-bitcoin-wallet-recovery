#!/usr/bin/env python3
import json
from datetime import datetime

def main():
    # Load wallet data
    with open('wallet_clean.json', 'r') as f:
        wallet_data = json.load(f)
    
    # Addresses with confirmed balances
    funded_addresses = {
        "13cHqB1vTx94NNxom8NwHgFfn6E7bnmnTq": {"balance": 0.04179530, "label": "Slush"},
        "1Nf4xvHEBcxUoZXRp9Fi6QrUp1TCK7wcDk": {"balance": 0.04014620, "label": "Eclipse"},
        "19rNsCg6BgpuZWJTAWB9kkhrj8QqfycdpD": {"balance": 0.02904965, "label": None},
        "19tpvtWxQ3cc7L3rWJqGiZbC9akEnLv2k7": {"balance": 0.01019683, "label": None},
        "1F2fvzHoL9jCSRxz5W1oa3mZUeyQKLmQhT": {"balance": 0.00026483, "label": None}
    }
    
    # Find private keys for funded addresses
    funded_keys = []
    for key_data in wallet_data['keys']:
        if key_data['addr'] in funded_addresses:
            funded_keys.append({
                'address': key_data['addr'],
                'balance': funded_addresses[key_data['addr']]['balance'],
                'label': funded_addresses[key_data['addr']]['label'],
                'private_key_wif': key_data['sec'],
                'private_key_hex': key_data['hexsec'],
                'compressed': key_data.get('compressed', False)
            })
    
    # Export to secure file
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'total_btc': sum(k['balance'] for k in funded_keys),
        'addresses': funded_keys
    }
    
    with open('funded_private_keys.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    # Create simple text file for easy import
    with open('private_keys_for_import.txt', 'w') as f:
        f.write("# Bitcoin Private Keys - KEEP SECURE!\n")
        f.write(f"# Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total Balance: {export_data['total_btc']:.8f} BTC\n")
        f.write("#\n")
        f.write("# Format: Address | Private Key (WIF) | Balance\n")
        f.write("# WIF keys can be imported directly into most wallets\n")
        f.write("#" + "="*70 + "\n\n")
        
        for key in funded_keys:
            label = f" ({key['label']})" if key['label'] else ""
            f.write(f"# {key['address']}{label}\n")
            f.write(f"# Balance: {key['balance']:.8f} BTC\n")
            f.write(f"{key['private_key_wif']}\n\n")
    
    print("=== PRIVATE KEY EXPORT COMPLETE ===")
    print(f"Total addresses with balance: {len(funded_keys)}")
    print(f"Total BTC: {export_data['total_btc']:.8f}")
    print("\nFiles created:")
    print("  - funded_private_keys.json (detailed export)")
    print("  - private_keys_for_import.txt (WIF format for easy import)")
    print("\n⚠️  SECURITY WARNING:")
    print("These files contain your private keys!")
    print("- Keep them secure and offline")
    print("- Delete them after importing to Coinbase")
    print("- Never share them with anyone")

if __name__ == "__main__":
    main()