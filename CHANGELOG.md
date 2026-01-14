# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-13

### Added

- **Claude Code Plugin Support**
  - Plugin manifest (`.claude-plugin/plugin.json`)
  - Marketplace configuration (`.claude-plugin/marketplace.json`)
  - Slash commands: `/recover-wallet`, `/scan-wallets`, `/check-balance`, `/detect-wallet`
  - Auto-activating skill for Bitcoin recovery context

- **Security Improvements**
  - Path validation with sensitive directory warnings (HIGH-001 fix)
  - Bitcoin address format validation before API calls (HIGH-002 fix)
  - Security audit documentation (`docs/SECURITY_AUDIT.md`)

- **Documentation**
  - Plugin installation guide (`docs/PLUGIN_INSTALL.md`)
  - Comprehensive security audit report

### Changed

- Updated `requests` dependency to >=2.31.0 (CVE-2023-32681 fix)
- Updated `cryptography` dependency to >=41.0.0 (multiple CVE fixes)
- Improved error handling for invalid paths and addresses

### Security

- Input validation for all user-provided file paths
- Symlink detection and warning
- System directory scan protection
- Bitcoin address format validation (legacy, P2SH, bech32)

## [1.0.0] - 2024-12-29

### Added

- Initial release
- Recovery wizard (`recovery_wizard.py`)
- Wallet detection (`lib/wallet_detector.py`)
- Multi-API balance checking (`lib/balance_checker.py`)
- Secure key export (`lib/secure_exporter.py`)
- Modified PyWallet with Python 3 support
- Directory scanning with progress tracking
- Support for encrypted wallet export
