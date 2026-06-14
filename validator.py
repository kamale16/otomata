"""
validator.py — Validasi input menggunakan Regular Expression
Konsep TBO: Regular Language yang dikenali oleh Finite Automaton
Teorema: Regex ≡ Regular Grammar ≡ DFA/NFA (Kleene's Theorem)
"""

import re

# ===== REGULAR EXPRESSION PATTERNS =====

# Email: nama@domain.tld
PATTERN_EMAIL = r'^[\w\.\-\+]+@([\w\-]+\.)+[a-zA-Z]{2,}$'

# Nomor HP Indonesia: 08xx / +62xx
PATTERN_PHONE = r'^(?:\+62|0)8[1-9][0-9]{7,10}$'

# Kode Tiket: EVT-AAA-0000
PATTERN_KODE_TIKET = r'^EVT-[A-Z]{3}-\d{4}$'

# Nama: huruf (termasuk aksen), spasi, titik, strip — 3 s.d. 60 karakter
PATTERN_NAMA = r'^[A-Za-z\s\.\-]{3,60}$'


def validate_email(email: str) -> tuple[bool, str]:
    email = email.strip()
    if re.match(PATTERN_EMAIL, email):
        return True, f"✅ Email **{email}** valid."
    return False, "❌ Format email tidak valid.\n> Contoh yang benar: `nama@email.com`"


def validate_phone(phone: str) -> tuple[bool, str]:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if re.match(PATTERN_PHONE, phone):
        return True, f"✅ Nomor HP **{phone}** valid."
    return False, "❌ Nomor HP tidak valid.\n> Format: `08xxxxxxxxxx` atau `+62xxxxxxxxx`"


def validate_kode_tiket(kode: str) -> tuple[bool, str]:
    kode = kode.strip().upper()
    if re.match(PATTERN_KODE_TIKET, kode):
        return True, f"✅ Format kode **{kode}** valid."
    return False, "❌ Format kode tiket salah.\n> Contoh yang benar: `EVT-TBO-1234`"


def validate_nama(nama: str) -> tuple[bool, str]:
    nama = nama.strip()
    if re.match(PATTERN_NAMA, nama):
        return True, f"✅ Nama **{nama}** diterima."
    return False, "❌ Nama hanya boleh berisi huruf dan spasi, minimal 3 karakter."


def get_pattern_info() -> dict:
    return {
        "Email": {
            "pattern": PATTERN_EMAIL,
            "contoh":  "nama@email.com",
            "ket":     "Format email standar (RFC 5321)",
        },
        "Nomor HP": {
            "pattern": PATTERN_PHONE,
            "contoh":  "08123456789",
            "ket":     "Nomor HP Indonesia (10–13 digit)",
        },
        "Kode Tiket": {
            "pattern": PATTERN_KODE_TIKET,
            "contoh":  "EVT-TBO-2025",
            "ket":     "Format kode tiket event",
        },
        "Nama": {
            "pattern": PATTERN_NAMA,
            "contoh":  "Budi Santoso",
            "ket":     "Huruf & spasi, 3–60 karakter",
        },
    }
