#!/bin/bash
# Complete GitHub publication script

echo "🚀 Publishing Bitcoin Wallet Recovery Tool to GitHub"
echo "=================================================="
echo ""

# Navigate to project directory
cd /home/josh/Projects/pywallet

# Step 1: Initialize git
echo "📁 Step 1: Initializing git repository..."
git init
echo "✅ Git initialized"
echo ""

# Step 2: Add all files
echo "📁 Step 2: Adding files to git..."
git add .
echo "✅ Files added"
echo ""

# Step 3: Create initial commit
echo "📁 Step 3: Creating initial commit..."
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
echo ""

# Step 4: Rename branch to main
echo "📁 Step 4: Setting default branch to main..."
git branch -M main
echo "✅ Branch renamed to main"
echo ""

# Step 5: Show instructions for GitHub
echo "📁 Step 5: Next steps for GitHub..."
echo "=================================="
echo ""
echo "1️⃣  Create a new repository on GitHub:"
echo "   👉 Go to: https://github.com/new"
echo "   "
echo "   Repository name: simple-bitcoin-wallet-recovery"
echo "   Description: Recover Bitcoin from old wallet.dat files - Successfully recovered 0.12+ BTC"
echo "   ✅ Public"
echo "   ❌ DON'T initialize with README, .gitignore, or license"
echo "   "
echo "   Click 'Create repository'"
echo ""
echo "2️⃣  After creating the repo, copy the commands GitHub shows you, which should be:"
echo "   "
echo "   git remote add origin https://github.com/YOUR_USERNAME/simple-bitcoin-wallet-recovery.git"
echo "   git push -u origin main"
echo ""
echo "3️⃣  Replace YOUR_USERNAME with your actual GitHub username and run those commands"
echo ""
echo "📌 Ready to push! Create the repository on GitHub first, then run the commands above."