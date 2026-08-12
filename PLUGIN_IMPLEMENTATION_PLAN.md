# Bitcoin Wallet Recovery - Claude Code Plugin Implementation Plan

## Executive Summary

This plan covers transforming the Simple Bitcoin Wallet Recovery tool into a Claude Code plugin with:
1. Full security audit of existing codebase
2. Plugin architecture design and implementation
3. Documentation for GitHub-based distribution
4. Installation instructions for end users

---

## Phase 1: Security Audit

### 1.1 Code Review Scope

#### Input Validation
| File | Risk Area | Check |
|------|-----------|-------|
| `recovery_wizard.py` | `--scandir` path argument | Path traversal, symlink attacks |
| `recovery_wizard.py` | `--wallet` file argument | Path traversal, file type validation |
| `lib/wallet_detector.py` | `analyze_file()` file_path | Arbitrary file read |
| `lib/balance_checker.py` | Bitcoin addresses | Address format validation |
| `pywallet.py` | `--wallet` argument | Command injection via subprocess |

#### Command Injection
| File | Line | Code Pattern | Risk |
|------|------|--------------|------|
| `recovery_wizard.py` | 276-282 | `subprocess.run([sys.executable, 'pywallet.py', ...])` | Low - uses list form |
| `lib/secure_exporter.py` | 396 | `subprocess.run(['shred', ...])` | Low - uses list form |

#### Sensitive Data Handling
| Concern | Files | Check |
|---------|-------|-------|
| Private keys in memory | `recovery_wizard.py`, `pywallet.py` | Memory clearing after use |
| Private keys on disk | `lib/secure_exporter.py` | File permissions (600) |
| Private keys in logs | All files | No logging of key material |
| API responses cached | `lib/balance_checker.py` | Cache contains addresses only |

#### Network Security
| Concern | Current State | Recommendation |
|---------|---------------|----------------|
| HTTPS usage | All APIs use HTTPS | ✓ Good |
| Certificate validation | Default requests behavior | ✓ Good |
| API key exposure | No API keys required | ✓ Good |
| Rate limiting | Implemented per-API | ✓ Good |

### 1.2 Dependency Audit

```
bsddb3>=6.2.9          - Berkeley DB bindings (native code)
ecdsa>=0.19.0          - Pure Python ECDSA
requests>=2.25.0       - HTTP library
cryptography>=3.4.8    - Encryption (optional)
qrcode[pil]>=7.3       - QR generation (optional)
```

**Audit tasks:**
- [ ] Run `pip-audit` or `safety check` on dependencies
- [ ] Check CVE database for known vulnerabilities
- [ ] Review bsddb3 native code security
- [ ] Verify minimum versions have security patches

### 1.3 OWASP Top 10 Checklist

| OWASP Risk | Applicable? | Status |
|------------|-------------|--------|
| A01 Broken Access Control | Limited (local tool) | Review file permissions |
| A02 Cryptographic Failures | Yes (private keys) | Audit key handling |
| A03 Injection | Yes (file paths) | Audit input validation |
| A04 Insecure Design | Review | Architecture review |
| A05 Security Misconfiguration | Yes | Default settings review |
| A06 Vulnerable Components | Yes | Dependency audit |
| A07 Auth Failures | N/A (no auth) | - |
| A08 Data Integrity Failures | Limited | Review JSON parsing |
| A09 Logging Failures | Yes | Ensure no key logging |
| A10 SSRF | Limited (balance APIs) | Review API calls |

### 1.4 Specific Security Findings Template

```markdown
## Finding: [Title]
**Severity**: Critical / High / Medium / Low / Info
**File**: path/to/file.py
**Line(s)**: XX-YY
**Description**: What the issue is
**Impact**: What could happen
**Recommendation**: How to fix
**Code Before**: ```python ... ```
**Code After**: ```python ... ```
```

---

## Phase 2: Plugin Architecture

### 2.1 Plugin Directory Structure

```
simple-bitcoin-wallet-recovery/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── recover-wallet.md        # Main recovery command
│   ├── scan-wallets.md          # Directory scanning
│   ├── check-balance.md         # Balance checking
│   └── detect-wallet.md         # Single file detection
├── agents/
│   └── wallet-recovery-expert.md # Expert agent for complex cases
├── skills/
│   └── bitcoin-recovery/
│       └── SKILL.md             # Auto-activating skill
├── hooks/
│   ├── hooks.json               # Security warning hooks
│   └── scripts/
│       └── security-warning.sh  # Pre-execution warning
│
│ # Existing tool files (unchanged locations)
├── recovery_wizard.py
├── pywallet.py
├── lib/
│   ├── __init__.py
│   ├── wallet_detector.py
│   ├── balance_checker.py
│   └── secure_exporter.py
├── requirements.txt
├── setup.py
└── docs/
```

### 2.2 Plugin Manifest

```json
{
  "name": "bitcoin-wallet-recovery",
  "version": "2.0.0",
  "description": "Recover Bitcoin from old wallet.dat files - detect wallets, extract keys, check balances",
  "author": {
    "name": "Josh Stephens",
    "url": "https://github.com/josh-stephens"
  },
  "repository": "https://github.com/josh-stephens/simple-bitcoin-wallet-recovery",
  "license": "MIT",
  "keywords": ["bitcoin", "wallet", "recovery", "cryptocurrency", "private-keys"]
}
```

### 2.3 Command Definitions

#### `/recover-wallet` (Primary Command)
```yaml
name: recover-wallet
description: Recover Bitcoin from wallet.dat files - scan directories or check single files
arguments:
  - name: path
    description: Path to wallet file or directory to scan
    required: true
  - name: dry-run
    description: Preview what would be scanned without processing
    required: false
```

#### `/scan-wallets`
```yaml
name: scan-wallets
description: Scan a directory recursively for potential Bitcoin wallet files
arguments:
  - name: directory
    description: Directory path to scan
    required: true
```

#### `/check-balance`
```yaml
name: check-balance
description: Check Bitcoin balance for an address using multiple blockchain APIs
arguments:
  - name: address
    description: Bitcoin address to check
    required: true
```

#### `/detect-wallet`
```yaml
name: detect-wallet
description: Analyze a file to determine if it's a Bitcoin wallet
arguments:
  - name: file
    description: Path to file to analyze
    required: true
```

### 2.4 Agent Definition

**wallet-recovery-expert.md** - Specialized agent for:
- Guiding users through complex recovery scenarios
- Handling encrypted wallets
- Troubleshooting Berkeley DB issues
- Explaining transfer procedures
- Security best practices

### 2.5 Skill Definition

**bitcoin-recovery/SKILL.md** - Auto-activates when:
- User mentions "wallet.dat", "bitcoin recovery", "old wallet"
- User has .dat files in context
- User asks about private key export

### 2.6 Hook Definition

**Pre-execution security warning** - Displays warning before:
- Exporting private keys
- Writing sensitive files
- Running recovery on production wallets

---

## Phase 3: Implementation Tasks

### 3.1 Security Fixes (from audit)

| Priority | Task | File(s) |
|----------|------|---------|
| High | Add path validation/sanitization | `recovery_wizard.py` |
| High | Validate Bitcoin address format | `lib/balance_checker.py` |
| Medium | Add memory clearing for keys | `recovery_wizard.py` |
| Medium | Review file permission handling | `lib/secure_exporter.py` |
| Low | Add input length limits | All input handlers |

### 3.2 Plugin Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `.claude-plugin/plugin.json` | Plugin manifest | Required |
| `commands/recover-wallet.md` | Main command | Required |
| `commands/scan-wallets.md` | Directory scan | Required |
| `commands/check-balance.md` | Balance check | Optional |
| `commands/detect-wallet.md` | File detection | Optional |
| `agents/wallet-recovery-expert.md` | Expert agent | Optional |
| `skills/bitcoin-recovery/SKILL.md` | Auto-skill | Recommended |
| `hooks/hooks.json` | Security hooks | Recommended |

### 3.3 Documentation Updates

| File | Changes |
|------|---------|
| `README.md` | Add plugin installation section |
| `CLAUDE.md` | Add plugin-specific guidance |
| `docs/PLUGIN_INSTALL.md` | New - detailed installation guide |
| `docs/SECURITY_AUDIT.md` | New - audit findings and mitigations |
| `CHANGELOG.md` | New - version history |

---

## Phase 4: GitHub Distribution (Marketplace)

### 4.1 Claude Code Marketplace Overview

Claude Code uses a **decentralized marketplace model**:
- No central app store - marketplaces are hosted on GitHub/GitLab
- Users add marketplaces, then install plugins from them
- Official marketplace: `claude-plugins-official` (pre-installed by Anthropic)

### 4.2 Marketplace Configuration

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "bitcoin-recovery-tools",
  "owner": {
    "name": "Josh Stephens",
    "email": "josh.stephens@gmail.com",
    "url": "https://github.com/josh-stephens"
  },
  "description": "Bitcoin wallet recovery tools for Claude Code",
  "plugins": [
    {
      "name": "bitcoin-wallet-recovery",
      "source": ".",
      "description": "Recover Bitcoin from old wallet.dat files - detect wallets, extract keys, check balances",
      "version": "2.0.0",
      "author": "Josh Stephens",
      "license": "MIT",
      "keywords": ["bitcoin", "wallet", "recovery", "cryptocurrency", "private-keys"],
      "category": "utilities",
      "homepage": "https://github.com/josh-stephens/simple-bitcoin-wallet-recovery"
    }
  ]
}
```

### 4.3 Repository Preparation

```bash
# Ensure clean state
git status

# Tag release version
git tag -a v2.0.0 -m "Release v2.0.0 - Claude Code plugin support"

# Push with tags
git push origin master --tags
```

### 4.4 User Installation Flow

**Step 1: Add the marketplace**
```bash
/plugin marketplace add josh-stephens/simple-bitcoin-wallet-recovery
```

**Step 2: Install the plugin**
```bash
/plugin install bitcoin-wallet-recovery@bitcoin-recovery-tools
```

**Alternative: One-liner if marketplace structure allows**
```bash
# Users can also browse after adding
/plugin list marketplaces
```

**Scope options** (users choose):
- **User scope**: Available across all projects (default)
- **Project scope**: Shared with collaborators via `.claude/settings.json`
- **Local scope**: Personal to specific repository

### 4.5 Release Checklist

- [ ] All security issues addressed
- [ ] `.claude-plugin/plugin.json` valid
- [ ] `.claude-plugin/marketplace.json` valid
- [ ] All commands tested
- [ ] README updated with marketplace installation instructions
- [ ] CHANGELOG created
- [ ] Version tagged in git
- [ ] Repository public (or accessible to intended users)
- [ ] LICENSE file present
- [ ] Dependencies documented

### 4.6 User Installation Guide (for docs)

```markdown
## Installing Bitcoin Wallet Recovery Plugin for Claude Code

### Prerequisites
- Claude Code CLI installed
- Python 3.7+
- Berkeley DB libraries (see platform-specific instructions below)

### Quick Install (2 commands)

**Step 1: Add the marketplace**
```bash
/plugin marketplace add josh-stephens/simple-bitcoin-wallet-recovery
```

**Step 2: Install the plugin**
```bash
/plugin install bitcoin-wallet-recovery@bitcoin-recovery-tools
```

**Step 3: Verify installation**
```bash
/plugin list
# Should show: bitcoin-wallet-recovery@bitcoin-recovery-tools (enabled)
```

### Install Python Dependencies

After plugin installation, install required Python packages:
```bash
# Navigate to plugin directory
cd ~/.claude/plugins/cache/simple-bitcoin-wallet-recovery/*/

# Install dependencies
pip install -r requirements.txt
```

### Platform-Specific Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-bsddb3 libdb-dev
pip install -r requirements.txt
```

**macOS:**
```bash
brew install berkeley-db
pip install bsddb3
pip install -r requirements.txt
```

**Windows:**
```powershell
# Install via pip (may require Visual C++ Build Tools)
pip install bsddb3
pip install -r requirements.txt
```
See docs/WINDOWS_INSTALL.md for detailed Windows instructions.

### Available Commands

After installation, these commands are available:
- `/recover-wallet <path>` - Main recovery wizard
- `/scan-wallets <directory>` - Scan for wallet files
- `/check-balance <address>` - Check Bitcoin address balance
- `/detect-wallet <file>` - Analyze if file is a Bitcoin wallet

### Updating the Plugin

```bash
/plugin marketplace update simple-bitcoin-wallet-recovery
```

### Uninstalling

```bash
/plugin uninstall bitcoin-wallet-recovery@bitcoin-recovery-tools
/plugin marketplace remove simple-bitcoin-wallet-recovery
```
```

### 4.7 Team/Organization Distribution

For private or team distribution:

**Option A: Private GitHub repo**
- Users need `GITHUB_TOKEN` environment variable set
- Works automatically with GitHub authentication

**Option B: Pre-configure in project settings**
Add to `.claude/settings.json` in your team's repos:
```json
{
  "extraKnownMarketplaces": {
    "simple-bitcoin-wallet-recovery": {
      "source": {"source": "github", "repo": "josh-stephens/simple-bitcoin-wallet-recovery"}
    }
  },
  "enabledPlugins": {
    "bitcoin-wallet-recovery@bitcoin-recovery-tools": true
  }
}
```

---

## Phase 5: Testing Plan

### 5.1 Plugin Testing

| Test | Command | Expected |
|------|---------|----------|
| Plugin loads | Start Claude Code | No errors, commands available |
| Help text | `/recover-wallet --help` | Shows usage |
| Dry run | `/scan-wallets /tmp --dry-run` | Lists files, no processing |
| Detection | `/detect-wallet test.dat` | Returns confidence score |
| Balance | `/check-balance 1A1zP1...` | Returns balance info |

### 5.2 Security Testing

| Test | Method | Expected |
|------|--------|----------|
| Path traversal | `--scandir ../../../etc` | Rejected or sandboxed |
| Large file | 10GB .dat file | Handled gracefully |
| Malformed wallet | Corrupted .dat | Error message, no crash |
| Invalid address | `/check-balance notanaddress` | Validation error |

### 5.3 Integration Testing

| Scenario | Steps | Expected |
|----------|-------|----------|
| Full recovery | Scan → Detect → Extract → Check → Export | Complete workflow |
| Empty wallet | Process wallet with 0 balance | Report shows empty |
| Encrypted wallet | Process encrypted wallet.dat | Encryption detected, guidance given |

---

## Timeline Estimate

| Phase | Tasks | Effort |
|-------|-------|--------|
| Phase 1: Security Audit | Code review, dependency audit, findings doc | 4-6 hours |
| Phase 2: Plugin Design | Architecture, manifest, command specs | 2-3 hours |
| Phase 3: Implementation | Create plugin files, apply security fixes | 4-6 hours |
| Phase 4: Documentation | README, install guide, changelog | 2-3 hours |
| Phase 5: Testing | Plugin testing, security testing | 2-4 hours |
| **Total** | | **14-22 hours** |

---

## Approval Checklist

Before proceeding, confirm:

- [ ] Security audit scope is acceptable
- [ ] Plugin command structure meets needs
- [ ] GitHub distribution approach is suitable
- [ ] Timeline expectations are reasonable

---

## Next Steps

1. **Approve this plan** or request modifications
2. **Begin Phase 1**: Security audit of existing code
3. **Review findings**: Discuss any critical issues before proceeding
4. **Implement phases 2-5** based on audit results

