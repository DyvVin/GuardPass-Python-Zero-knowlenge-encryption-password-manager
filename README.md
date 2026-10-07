# GuardPass | Python Desktop Password Manager

A secure, localized, Zero-Knowledge desktop password manager built on Python using graphic interface library PyQt6 and SQLite. It uses an asynchronous background layer QThread for dynamic performance, combined with an automated structural database security auditor.

---

**Tech Stack & Dependencies**

- Frontend: Python 3.10+, PyQt6
- Database Engine: SQLite 3 
- Cryptography Engine: "Cryptography" Python package 

---

**Cryptography and security logic**

Based on Zero-Knowledge operational model GurdPass does not use raw credentials, master passwords, or encryption keys, which are also not written to the local disk, or transmitted over any network. 

**Cryptographic pipeline scheme:**

[ User Master Password ] ──► [ PBKDF2 + SHA-256 + 100k Iterations ] + [ Cryptographic Salt ]

├──►[ 256-bit AES Encryption Key ] ──( Cached in Memory / RAM )

├──► [ AES-256-GCM Encrypt ] ──► Base64 String ──► [ SQLite Disk Store ]

└──► [ AES-256-GCM Decrypt ] ◄── Base64 String ◄── [ SQLite Disk Store ]

**1. Key Derivation Function (PBKDF2-HMAC-SHA256)**
Defence against automated local dictionary attacks and offline brute-forcing logic:
* Salting: Upon initial run, a 16-byte random salt is generated using `os.urandom()`. This salt prevents the application of pre-computed cryptographic lookup sheets (Rainbow tables).
* Key Stretching: The user's master password string is combined with the salt and subjected to 100,000 sequential iterations of the SHA-256 hashing function.

**2. Authenticated Symmetric Encryption (AES-256-GCM)**
Confidential records (Logins and Passwords) are secured using AES operating in GCM.
* AEAD Protocol: GCM generates a discrete cryptographic verification tag alongside raw bit concealment, if an external process attempts to modify or patch any of cipher-text directly within the "guardpass.db" SQLite file, the AES decryption engine flags the integrity violation, aborting the payload read operation.
* Cryptographic Nonce: Every entry invocation calculates a 12-byte random initialization vector (nonce) to guarantee that same source texts saved twice (e.g., repeating a common backup password across different profiles) result in different output cipher-strings, reducing statistical analysis attacks.

**3. Blind Duplicate Detection (MD5 Verification Hashes)**
The security audit panel parses credentials for cross-account reuse. Logic to maintain maximum performance without RAM safety hazards:
* During record storage, the application takes the unencrypted password string, creates a one-way MD5 hash, and writes it into an isolated SQLite table index column. MD5 cannot be reversed to extract the plain password text, but identical source strings produce identical MD5 hashes.
* Database Aggregation:
  ```sql
  SELECT COUNT(*) FROM accounts GROUP BY password_hash_md5 HAVING COUNT(*) > 1
  ```

---

**Project Architecture**

```text
guardpass/
└── Password_Manager/
    ├── main.py                # Main application entry point & orchestration
    │
    ├── database/              
    │   ├── connection.py      # Database configurations
    │   ├── models.py          # Schemas generation instructions
    │   └── repository.py      # CRUD logic
    │
    ├── crypto/                
    │   ├── key_derivation.py  # PBKDF2 stretching algorithms
    │   └── encryptor.py       # AES-GCM encryption engines
    │
    ├── services/              
    │   ├── auth_service.py    # All session and master-password logic
    │   └── auditor.py         # Overall database security scanner
    │
    └── ui/                    
        ├── styles.py          # QSS global design
        ├── auth_window.py     # Initial authorization window
        ├── main_window.py     # Frontend functionality
        └── threads.py         # QThread isolation
```

---

# Security Audit Score Algorithm (will be renovated in future updates)

The security audit system calculates an overall security index score starting at 100% (perfect safety), for each structural weakness found, penalties are deducted according to the following weight rules:

1. Weak Passwords Check: Credential containing fewer than 8 characters is flagged as a security flaw. **Penalty: -15 points per entry**
2. Reused Passwords Check: Same passwords get detected by being flagged via the index MD5 grouping check. **Penalty: -10 points per entry**

Evaluation logic:
```python
penalty = (weak_passwords * 15) + (reused_passwords * 10)
security_score = max(0, 100 - penalty)
```

---

# Installation & Local Execution

Install core PyOt6 and cryptography libraries using commands below and execute Guardpass.exe file

```bash
  pip install PyQt6
  pip install cryptography
```

---

# Future features

1. Restructured audit logic: add capital letters, special symbols and didgits criteria.
2. Field on first program boot with which user can choose .db file generation path (or leave %AppData% as defualt).
3. Master-password restoration function via Google account.
4. Built-in secure password generator to suggest a replacemnt of "weak" passwords.
5. More graphical indicators to optimize app usage.
6. Final code refractoring and optimization.
