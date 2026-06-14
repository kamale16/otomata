"""
grammar.py — Context-Free Grammar (CFG) untuk parsing perintah user
Konsep TBO: CFG (Tipe 2 Chomsky) lebih powerful dari Regular Language (Tipe 3)
Parsing menggunakan Early-style top-down matching + stemming sederhana Bahasa Indonesia
"""

# ===== STEMMING SEDERHANA (awalan Bahasa Indonesia) =====
# Menangani imbuhan: me-, di-, ber-, ter-, ke-, -kan, -i, -an
PREFIXES = ("mendaftar", "daftarkan", "mendaftarkan", "didaftarkan",
            "melihat", "tampilkan", "ditampilkan",
            "cekkan", "mengecek", "dicek",
            "batalkan", "membatalkan", "dibatalkan",
            "keluar", "keluarkan")

STEM_MAP = {
    # Variasi verb → stem
    "daftarkan": "daftar", "mendaftar": "daftar", "mendaftarkan": "daftar",
    "didaftarkan": "daftar", "ikutan": "daftar", "ikutin": "daftar",
    "melihat": "lihat", "tampilkan": "lihat", "ditampilkan": "lihat",
    "tunjukkan": "lihat", "perlihatkan": "lihat", "kasih lihat": "lihat",
    "mengecek": "cek", "cekkan": "cek", "dicek": "cek", "periksa": "cek",
    "batalkan": "batal", "membatalkan": "batal", "cancel": "batal",
    "keluarkan": "keluar", "selesaikan": "selesai",
    # Variasi noun → canonical
    "konferensi": "event", "seminar": "event", "workshop": "event",
    "acara": "event", "kegiatan": "event",
    "kode": "tiket", "booking": "tiket", "reservasi": "tiket",
    "sesi": "jadwal", "speaker": "jadwal", "pembicara": "jadwal",
    "narasumber": "jadwal", "agenda": "jadwal", "rundown": "jadwal",
    "tempat": "venue", "lokasi": "venue", "ruangan": "venue",
    "gedung": "venue", "alamat": "venue", "peta": "venue",
    "pertanyaan": "faq", "help": "faq",
    "bantuan": "faq", "informasi": "venue",
}

# ===== TERMINAL SYMBOLS =====
# VP (Verb Phrase) terminals
VERBS = {
    "daftar", "registrasi", "ikut", "join", "masuk", "gabung",
    "lihat", "tampil", "cek", "show", "buka", "info",
    "batal", "cancel",
    "keluar", "exit", "selesai", "done", "tutup",
}

# NP (Noun Phrase) terminals → intent
NOUN_TO_INTENT = {
    "event":   "registrasi",
    "tiket":   "cek_tiket",
    "jadwal":  "jadwal",
    "venue":   "venue",
    "faq":     "faq",
}

VERB_TO_INTENT = {
    "daftar":    "registrasi", "registrasi": "registrasi",
    "ikut":      "registrasi", "join":       "registrasi",
    "masuk":     "registrasi", "gabung":     "registrasi",
    "lihat":     "jadwal",     "tampil":     "jadwal",
    "cek":       "cek_tiket",  "show":       "jadwal",
    "buka":      "venue",      "info":       "venue",
    "batal":     "cancel",     "cancel":     "cancel",
    "keluar":    "exit",       "exit":       "exit",
    "selesai":   "exit",       "done":       "exit",
    "tutup":     "exit",
}

# ===== CFG PRODUCTIONS =====
# S  → VP NP | VP | NP
# VP → v  (v ∈ VERBS)
# NP → n  (n ∈ NOUN_TO_INTENT.keys())
CFG_PRODUCTIONS = {
    "S":  ["VP NP", "VP", "NP"],
    "VP": sorted(VERBS),
    "NP": sorted(NOUN_TO_INTENT.keys()),
}

# Stop words Bahasa Indonesia
STOPWORDS = {
    "saya", "aku", "gue", "kamu", "kita", "kami",
    "mau", "minta", "tolong", "bisa", "dong", "nih",
    "kan", "ya", "yuk", "ingin", "mohon", "untuk",
    "ke", "di", "dari", "dan", "atau", "yang", "dengan",
    "ini", "itu", "ada", "adalah", "juga", "lagi", "dong",
    "please", "please", "the", "a", "an", "i", "want",
}


def stem(word: str) -> str:
    """Kembalikan stem dari sebuah kata menggunakan STEM_MAP."""
    return STEM_MAP.get(word.lower(), word.lower())


def tokenize(kalimat: str) -> list[str]:
    """Tokenisasi + hapus stopwords + stem."""
    raw_tokens = kalimat.lower().strip().split()
    result = []
    for t in raw_tokens:
        # hapus tanda baca
        t_clean = t.strip(".,!?;:'\"()")
        if t_clean and t_clean not in STOPWORDS:
            result.append(stem(t_clean))
    return result


def parse(kalimat: str) -> dict:
    """
    Parse kalimat user menggunakan CFG (S → VP NP | VP | NP).
    Menerapkan stemming sebelum pencocokan terminal.
    
    Returns:
        intent  : str | None  — intent yang terdeteksi
        tokens  : list[str]   — token setelah stemming & stopword removal
        verb    : str | None  — verb terminal yang cocok
        noun    : str | None  — noun terminal yang cocok
        rule    : str         — produksi CFG yang dipakai
        matched : bool
    """
    tokens = tokenize(kalimat)
    found_verb = None
    found_noun = None

    for token in tokens:
        if token in VERBS and not found_verb:
            found_verb = token
        if token in NOUN_TO_INTENT and not found_noun:
            found_noun = token

    # Tentukan rule & intent
    if found_verb and found_noun:
        rule = "S → VP NP"
        # Jika verb adalah query (lihat/cek), prioritaskan noun intent
        if found_verb in {"lihat", "tampil", "cek", "show", "buka", "info"}:
            intent = NOUN_TO_INTENT.get(found_noun)
        else:
            intent = VERB_TO_INTENT.get(found_verb) or NOUN_TO_INTENT.get(found_noun)
    elif found_verb:
        rule = "S → VP"
        intent = VERB_TO_INTENT.get(found_verb)
    elif found_noun:
        rule = "S → NP"
        intent = NOUN_TO_INTENT.get(found_noun)
    else:
        rule = "S → ε (tidak cocok)"
        intent = None

    return {
        "intent":  intent,
        "tokens":  tokens,
        "verb":    found_verb,
        "noun":    found_noun,
        "rule":    rule,
        "matched": intent is not None,
    }


def intent_to_menu_choice(intent: str) -> str | None:
    """Konversi intent → angka pilihan menu."""
    return {
        "registrasi": "1",
        "jadwal":     "2",
        "cek_tiket":  "3",
        "venue":      "4",
        "faq":        "5",
    }.get(intent)


def get_cfg_info() -> dict:
    """Kembalikan info CFG untuk ditampilkan di UI."""
    return {
        "productions": CFG_PRODUCTIONS,
        "verbs":       sorted(VERBS),
        "nouns":       sorted(NOUN_TO_INTENT.keys()),
        "stem_map":    STEM_MAP,
    }
