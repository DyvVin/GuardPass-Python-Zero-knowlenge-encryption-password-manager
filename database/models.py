CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS master_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verification_hash TEXT NOT NULL,
    crypto_salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT,
    login TEXT NOT NULL,
    encrypted_password TEXT NOT NULL,
    password_length INTEGER NOT NULL,
    password_hash_md5 TEXT NOT NULL,  -- Нужен для быстрого поиска дубликатов SQL GROUP BY
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
