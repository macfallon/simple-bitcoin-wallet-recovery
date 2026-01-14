# Security Audit Report

**Project**: Simple Bitcoin Wallet Recovery
**Audit Date**: 2026-01-13
**Auditor**: Claude Code Security Review
**Scope**: Full code audit - input validation, sensitive data handling, dependencies, OWASP considerations

---

## Executive Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 0 | - |
| High | 2 | Requires fix before release |
| Medium | 4 | Recommended fixes |
| Low | 3 | Minor improvements |
| Info | 2 | Observations |

**Overall Assessment**: The codebase follows reasonable security practices for a local recovery tool. No critical vulnerabilities found. Two high-severity issues related to input validation should be addressed before public release.

---

## Findings

### HIGH-001: No Path Validation on User Input

**Severity**: High
**Files**: `recovery_wizard.py` (lines 549-571)
**CWE**: CWE-22 (Path Traversal)

**Description**:
User-supplied paths from `--scandir` and `--wallet` arguments are used directly without validation. While `Path.exists()` is checked, there's no protection against:
- Path traversal attacks (`../../../etc/passwd`)
- Symlink following to sensitive directories
- Scanning system directories unintentionally

**Impact**:
An attacker could craft a malicious path to read files outside intended directories, or a user could accidentally scan system directories exposing sensitive data.

**Current Code**:
```python
if args.scandir:
    scan_path = Path(args.scandir)
    if not scan_path.exists():
        print(f"❌ Error: Directory '{scan_path}' does not exist")
        sys.exit(1)
    # No further validation - path is used directly
    dat_files = wizard.scan_directory(scan_path, dry_run=args.dry_run)
```

**Recommendation**:
```python
import os

def validate_scan_path(path: Path) -> Path:
    """Validate and sanitize user-provided scan path"""
    # Resolve to absolute path
    resolved = path.resolve()

    # Check it exists
    if not resolved.exists():
        raise ValueError(f"Path does not exist: {path}")

    # Check it's a directory (for scandir)
    if not resolved.is_dir():
        raise ValueError(f"Not a directory: {path}")

    # Warn about sensitive directories
    sensitive_prefixes = ['/etc', '/var', '/root', 'C:\\Windows', 'C:\\Program Files']
    for prefix in sensitive_prefixes:
        if str(resolved).startswith(prefix):
            print(f"⚠️  Warning: Scanning system directory {resolved}")
            response = input("Continue? (y/N): ")
            if response.lower() != 'y':
                raise ValueError("Scan cancelled by user")

    return resolved
```

---

### HIGH-002: No Bitcoin Address Validation

**Severity**: High
**Files**: `lib/balance_checker.py` (lines 57, 103, 155-235)
**CWE**: CWE-20 (Improper Input Validation)

**Description**:
Bitcoin addresses are passed directly to API URLs without format validation. Malformed addresses could cause unexpected behavior or be used for URL injection.

**Current Code**:
```python
def _parse_blockchain_info(self, address: str, api_config: Dict) -> Optional[Dict]:
    url = api_config['url'].format(address)  # Direct string interpolation
    response = self.session.get(url, timeout=10)
```

**Impact**:
- API errors from malformed addresses
- Potential URL injection if address contains special characters
- Unnecessary API calls for invalid addresses

**Recommendation**:
```python
import re

def validate_bitcoin_address(address: str) -> bool:
    """Validate Bitcoin address format (basic validation)"""
    # Legacy addresses (P2PKH, P2SH)
    legacy_pattern = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'
    # Bech32 addresses (SegWit)
    bech32_pattern = r'^bc1[a-zA-HJ-NP-Z0-9]{25,89}$'

    if re.match(legacy_pattern, address):
        return True
    if re.match(bech32_pattern, address):
        return True
    return False

def check_balance(self, address: str, use_cache: bool = True) -> Dict:
    if not validate_bitcoin_address(address):
        return {
            'balance': 0,
            'error': 'Invalid Bitcoin address format',
            'verified': False
        }
    # ... rest of method
```

---

### MED-001: Broad Exception Handling

**Severity**: Medium
**Files**: `lib/balance_checker.py`, `lib/wallet_detector.py`, `lib/secure_exporter.py`
**CWE**: CWE-755 (Improper Handling of Exceptional Conditions)

**Description**:
Multiple bare `except:` clauses suppress all exceptions, making debugging difficult and potentially hiding security issues.

**Examples**:
```python
# balance_checker.py:308
except:
    pass

# secure_exporter.py:333
except:
    pass
```

**Recommendation**:
Replace bare `except:` with specific exception types:
```python
except (IOError, OSError, json.JSONDecodeError) as e:
    logging.debug(f"Cache operation failed: {e}")
    pass
```

---

### MED-002: Cache Files Without Restricted Permissions

**Severity**: Medium
**Files**: `lib/balance_checker.py` (lines 358-370)
**CWE**: CWE-732 (Incorrect Permission Assignment)

**Description**:
Balance cache files are created with default permissions. While they don't contain private keys, they do reveal which addresses were checked.

**Current Code**:
```python
def _cache_balance(self, address: str, balance_info: Dict):
    cache_file = self.cache_dir / f"{address}.json"
    with open(cache_file, 'w') as f:  # Default permissions
        json.dump({...}, f)
```

**Recommendation**:
```python
import os
import stat

def _cache_balance(self, address: str, balance_info: Dict):
    cache_file = self.cache_dir / f"{address}.json"
    with open(cache_file, 'w') as f:
        json.dump({...}, f)
    # Restrict permissions
    if os.name != 'nt':  # Unix
        os.chmod(cache_file, stat.S_IRUSR | stat.S_IWUSR)  # 600
```

---

### MED-003: subprocess Import Wildcard

**Severity**: Medium
**Files**: `pywallet.py` (line 82)
**CWE**: CWE-676 (Use of Potentially Dangerous Function)

**Description**:
The line `from subprocess import *` imports all subprocess functions including `call()` and `Popen()` which could be misused with `shell=True`. While no active code uses these dangerously, it's a code smell.

**Current Code**:
```python
from subprocess import *
```

**Recommendation**:
```python
import subprocess
# Or explicitly:
from subprocess import check_output, run, PIPE
```

---

### MED-004: Hardcoded Encryption Salt

**Severity**: Medium
**Files**: `lib/secure_exporter.py` (line 256)
**CWE**: CWE-329 (Not Using an Unpredictable IV with CBC Mode)

**Description**:
The encrypted export uses a hardcoded salt, reducing cryptographic security.

**Current Code**:
```python
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=b'bitcoin_wallet_salt',  # Hardcoded salt!
    iterations=100000,
)
```

**Recommendation**:
```python
import os

# Generate random salt
salt = os.urandom(16)

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)

# Store salt with encrypted file
with open(file_path, 'wb') as f:
    f.write(salt)  # First 16 bytes
    f.write(encrypted_data)
```

---

### LOW-001: No Rate Limit Backoff

**Severity**: Low
**Files**: `lib/balance_checker.py`
**CWE**: N/A

**Description**:
Rate limiting uses fixed delays but doesn't implement exponential backoff on API errors, which could lead to temporary bans from blockchain APIs.

**Recommendation**:
Implement exponential backoff on HTTP 429 (Too Many Requests) responses.

---

### LOW-002: Private Keys in Console Output

**Severity**: Low
**Files**: `pywallet.py` (lines 2927, 2930)
**CWE**: CWE-532 (Information Exposure Through Log Files)

**Description**:
When running pywallet directly, private keys may be printed to console/stdout, which could be captured in terminal history or logs.

**Current Code**:
```python
print("Privkey:             %s"%wif)
print("Hexprivkey:          %s"%bytes_to_str(binascii.hexlify(secret)))
```

**Recommendation**:
Add warning before displaying sensitive data, or require explicit `--show-private-keys` flag.

---

### LOW-003: Windows File Permissions Not Set

**Severity**: Low
**Files**: `lib/secure_exporter.py` (lines 328-334)
**CWE**: CWE-732

**Description**:
Secure file permissions (600) are only set on Unix systems. Windows files remain with default permissions.

**Current Code**:
```python
def _set_secure_permissions(self, file_path: Path):
    try:
        if platform.system() != 'Windows':
            os.chmod(file_path, 0o600)
    except:
        pass
```

**Recommendation**:
Add Windows ACL support using `pywin32` or `icacls`:
```python
if platform.system() == 'Windows':
    import subprocess
    subprocess.run(['icacls', str(file_path), '/inheritance:r',
                   '/grant:r', f'{os.getenv("USERNAME")}:F'],
                   capture_output=True)
```

---

### INFO-001: No Certificate Pinning

**Severity**: Info
**Files**: `lib/balance_checker.py`

**Description**:
HTTPS connections don't use certificate pinning. While all APIs use HTTPS (good), a sophisticated MITM attack could potentially intercept balance queries.

**Assessment**:
Acceptable for this use case. Balance queries are not sensitive, and certificate pinning would complicate deployment.

---

### INFO-002: User-Agent Reveals Tool Identity

**Severity**: Info
**Files**: `lib/balance_checker.py` (line 49)

**Description**:
The User-Agent header identifies the tool: `Simple-Bitcoin-Wallet-Recovery/1.0`

**Assessment**:
This is actually good practice - it helps API operators identify legitimate tools vs malicious scrapers.

---

## Dependency Analysis

| Package | Version Required | Known Vulnerabilities |
|---------|------------------|----------------------|
| bsddb3 | >=6.2.9 | None known (native code) |
| ecdsa | >=0.19.0 | None in specified versions |
| requests | >=2.25.0 | CVE-2023-32681 fixed in 2.31.0 - **recommend upgrading** |
| cryptography | >=3.4.8 | Multiple CVEs in older versions - **recommend >=41.0.0** |
| qrcode | >=7.3 | None known |

**Recommendation**: Update requirements.txt:
```
requests>=2.31.0
cryptography>=41.0.0
```

---

## OWASP Top 10 Assessment

| Risk | Status | Notes |
|------|--------|-------|
| A01 Broken Access Control | ⚠️ | Path validation needed (HIGH-001) |
| A02 Cryptographic Failures | ⚠️ | Hardcoded salt (MED-004) |
| A03 Injection | ⚠️ | Address validation needed (HIGH-002) |
| A04 Insecure Design | ✅ | Architecture is appropriate |
| A05 Security Misconfiguration | ⚠️ | Cache permissions (MED-002) |
| A06 Vulnerable Components | ⚠️ | Update dependencies |
| A07 Auth Failures | N/A | No authentication required |
| A08 Data Integrity Failures | ✅ | No unsafe deserialization |
| A09 Logging Failures | ⚠️ | Private key console output (LOW-002) |
| A10 SSRF | ✅ | APIs are hardcoded, no user-controlled URLs |

---

## Remediation Priority

### Before Public Release (Required)
1. **HIGH-001**: Add path validation for `--scandir` and `--wallet`
2. **HIGH-002**: Add Bitcoin address format validation
3. **Dependencies**: Update requests and cryptography versions

### Recommended Improvements
4. **MED-001**: Replace bare except clauses
5. **MED-002**: Set cache file permissions
6. **MED-003**: Use explicit subprocess imports
7. **MED-004**: Use random salt for encryption

### Optional Enhancements
8. **LOW-001**: Implement exponential backoff
9. **LOW-002**: Add flag for showing private keys
10. **LOW-003**: Add Windows ACL support

---

## Positive Security Practices Observed

1. ✅ Subprocess calls use list form (no shell injection)
2. ✅ All API calls use HTTPS
3. ✅ Private key files get restricted Unix permissions (600)
4. ✅ No eval/exec usage
5. ✅ JSON deserialization (not pickle)
6. ✅ Rate limiting implemented for API calls
7. ✅ Timeout on HTTP requests
8. ✅ Security warnings in exported files
9. ✅ Secure deletion option available

---

## Appendix: Files Reviewed

| File | Lines | Risk Level |
|------|-------|------------|
| recovery_wizard.py | 631 | Medium |
| pywallet.py | 4240+ | Medium |
| lib/balance_checker.py | 419 | Low |
| lib/wallet_detector.py | 307 | Low |
| lib/secure_exporter.py | 482 | Low |

---

*Report generated by Claude Code Security Review*
