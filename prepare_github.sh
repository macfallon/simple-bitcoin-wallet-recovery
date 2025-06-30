#!/bin/bash
# Prepare repository for GitHub publication

echo "🚀 Preparing Bitcoin Wallet Recovery Tool for GitHub"
echo "==================================================="

# Navigate to project directory
cd /home/josh/Projects/pywallet

# Step 1: Remove sensitive files
echo ""
echo "📁 Step 1: Removing sensitive files..."
echo "-------------------------------------"

# List files that will be removed
echo "Files to be removed:"
echo "  - wallet_dump.json (contains private keys)"
echo "  - wallet_clean.json (contains private keys)"
echo "  - another_wallet_clean.json (contains private keys)"
echo "  - funded_private_keys.json (contains funded private keys)"
echo "  - private_keys_for_import.txt (private keys for import)"
echo "  - electrum_import_keys.txt (Electrum import format)"
echo "  - wallet_addresses.txt (wallet addresses)"
echo "  - another_wallet_addresses.txt (wallet addresses)"
echo "  - Bitcoin data.zip (archive with sensitive data)"
echo "  - *.Zone.Identifier files (Windows metadata)"

# Ask for confirmation
read -p "Remove these sensitive files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    rm -f wallet_dump.json
    rm -f wallet_clean.json
    rm -f another_wallet_clean.json
    rm -f funded_private_keys.json
    rm -f private_keys_for_import.txt
    rm -f electrum_import_keys.txt
    rm -f wallet_addresses.txt
    rm -f another_wallet_addresses.txt
    rm -f "Bitcoin data.zip"
    rm -f *.Zone.Identifier
    rm -f tests/*.Zone.Identifier
    echo "✅ Sensitive files removed"
else
    echo "❌ Skipping file removal"
fi

# Step 2: Create demo wallet if needed
echo ""
echo "📁 Step 2: Checking demo wallet..."
echo "-------------------------------------"

if [ ! -f "tests/demo_wallet.dat" ]; then
    echo "Creating placeholder demo wallet..."
    # Create a minimal demo wallet file
    mkdir -p tests
    echo "DEMO WALLET PLACEHOLDER - Replace with actual testnet wallet" > tests/demo_wallet.dat
    echo "✅ Created placeholder demo wallet"
else
    echo "✅ Demo wallet already exists"
fi

# Step 3: Initialize git if needed
echo ""
echo "📁 Step 3: Initializing git repository..."
echo "-------------------------------------"

if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi

# Step 4: Add files to git
echo ""
echo "📁 Step 4: Adding files to git..."
echo "-------------------------------------"

git add .
echo "✅ Files added to staging area"

# Step 5: Show git status
echo ""
echo "📁 Step 5: Current git status..."
echo "-------------------------------------"
git status

# Step 6: Create commit
echo ""
echo "📁 Step 6: Creating initial commit..."
echo "-------------------------------------"

read -p "Create initial commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    git commit -m "Initial commit: Simple Bitcoin Wallet Recovery Tool

Success story: Recovered 0.12145281 BTC from an old wallet.dat file.
This tool streamlines the process for others to check their old drives.

Features:
- Universal .dat file detection with confidence scoring
- Multi-source balance verification (4 blockchain APIs)
- Secure key export in multiple formats (Electrum, Bitcoin Core, JSON, CSV)
- Directory scanning with progress tracking
- Organized output structure (funded vs empty wallets)
- Python 3 compatible

Usage: python3 recovery_wizard.py --scandir /path/to/old/drive

Security: Always work offline and transfer funds to a new wallet after recovery!"
    
    echo "✅ Initial commit created"
else
    echo "❌ Skipping commit creation"
fi

# Step 7: Instructions for GitHub
echo ""
echo "📁 Next Steps for GitHub Publication:"
echo "-------------------------------------"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name: simple-bitcoin-wallet-recovery"
echo "   - Description: \"Recover Bitcoin from old wallet.dat files - Successfully recovered 0.12+ BTC\""
echo "   - Make it public"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Add the remote repository:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/simple-bitcoin-wallet-recovery.git"
echo ""
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Add topics on GitHub:"
echo "   - bitcoin"
echo "   - wallet-recovery"
echo "   - cryptocurrency"
echo "   - bitcoin-wallet"
echo "   - python3"
echo ""
echo "5. Create a release:"
echo "   - Tag: v1.0.0"
echo "   - Title: \"Initial Release - Bitcoin Wallet Recovery Tool\""
echo "   - Include success story in release notes"
echo ""
echo "✅ Preparation complete! Your repository is ready for GitHub."