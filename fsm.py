"""
fsm.py — Finite State Machine untuk alur percakapan EventBot
Konsep TBO: DFA dengan states, alphabet input, fungsi transisi, start state, accept states

Formal definition: M = (Q, Σ, δ, q0, F)
"""

# ===== DEFINISI STATES (Q) =====
STATES = {
    "START",
    "MENU_UTAMA",
    "REGISTRASI_NAMA",
    "REGISTRASI_EMAIL",
    "REGISTRASI_TELEPON",
    "REGISTRASI_TIKET",
    "REGISTRASI_KONFIRMASI",
    "LIHAT_JADWAL",
    "CEK_TIKET",
    "INFO_VENUE",
    "FAQ",
    "ACCEPT",
    "REJECT",
}

# ===== START STATE (q0) =====
START_STATE = "START"

# ===== ACCEPT STATES (F) =====
ACCEPT_STATES = {"ACCEPT"}

# ===== REJECT STATE =====
REJECT_STATE = "REJECT"

# ===== FUNGSI TRANSISI (δ): state x symbol → next_state =====
TRANSITION_TABLE = {
    "START": {
        "*": "MENU_UTAMA",
    },
    "MENU_UTAMA": {
        "1": "REGISTRASI_NAMA",
        "2": "LIHAT_JADWAL",
        "3": "CEK_TIKET",
        "4": "INFO_VENUE",
        "5": "FAQ",
        "*": "MENU_UTAMA",
    },
    "REGISTRASI_NAMA": {
        "valid_nama": "REGISTRASI_EMAIL",
        "invalid":    "REJECT",
        "*":          "REGISTRASI_NAMA",
    },
    "REGISTRASI_EMAIL": {
        "valid_email": "REGISTRASI_TELEPON",
        "invalid":     "REJECT",
        "*":           "REGISTRASI_EMAIL",
    },
    "REGISTRASI_TELEPON": {
        "valid_phone": "REGISTRASI_TIKET",
        "invalid":     "REJECT",
        "*":           "REGISTRASI_TELEPON",
    },
    "REGISTRASI_TIKET": {
        "1": "REGISTRASI_KONFIRMASI",
        "2": "REGISTRASI_KONFIRMASI",
        "3": "REGISTRASI_KONFIRMASI",
        "*": "REGISTRASI_TIKET",
    },
    "REGISTRASI_KONFIRMASI": {
        "ya":    "ACCEPT",
        "tidak": "MENU_UTAMA",
        "*":     "REGISTRASI_KONFIRMASI",
    },
    "LIHAT_JADWAL": {
        "*": "MENU_UTAMA",
    },
    "CEK_TIKET": {
        "valid_kode": "ACCEPT",
        "invalid":    "REJECT",
        "*":          "CEK_TIKET",
    },
    "INFO_VENUE": {
        "*": "MENU_UTAMA",
    },
    "FAQ": {
        "*": "MENU_UTAMA",
    },
    "ACCEPT": {
        "*": "MENU_UTAMA",
    },
    "REJECT": {
        "*": "MENU_UTAMA",
    },
}

# State descriptions untuk UI
STATE_DESCRIPTIONS = {
    "START":                  "Titik awal, menunggu input pertama",
    "MENU_UTAMA":             "Menampilkan menu dan menunggu pilihan",
    "REGISTRASI_NAMA":        "Menunggu input nama peserta",
    "REGISTRASI_EMAIL":       "Menunggu input email (divalidasi regex)",
    "REGISTRASI_TELEPON":     "Menunggu input nomor HP (divalidasi regex)",
    "REGISTRASI_TIKET":       "Menunggu pilihan jenis tiket",
    "REGISTRASI_KONFIRMASI":  "Menunggu konfirmasi data registrasi",
    "LIHAT_JADWAL":           "Menampilkan jadwal konferensi",
    "CEK_TIKET":              "Menunggu kode tiket (divalidasi regex)",
    "INFO_VENUE":             "Menampilkan info venue & lokasi",
    "FAQ":                    "Menampilkan pertanyaan umum",
    "ACCEPT":                 "✅ Accept state — proses berhasil",
    "REJECT":                 "❌ Reject state — input tidak valid",
}

# State colors untuk visualisasi
STATE_COLORS = {
    "START":                 "#8888CC",
    "MENU_UTAMA":            "#6C63FF",
    "REGISTRASI_NAMA":       "#4A9EFF",
    "REGISTRASI_EMAIL":      "#4A9EFF",
    "REGISTRASI_TELEPON":    "#4A9EFF",
    "REGISTRASI_TIKET":      "#4A9EFF",
    "REGISTRASI_KONFIRMASI": "#4A9EFF",
    "LIHAT_JADWAL":          "#F5A623",
    "CEK_TIKET":             "#F5A623",
    "INFO_VENUE":            "#F5A623",
    "FAQ":                   "#F5A623",
    "ACCEPT":                "#43D9AD",
    "REJECT":                "#FF6584",
}


class EventBotFSM:
    """
    Implementasi DFA untuk chatbot manajemen event.
    M = (Q, Σ, δ, q0, F)
    """

    def __init__(self):
        self.current_state: str = START_STATE
        self.temp_data: dict = {}
        self.history: list[str] = [START_STATE]

    def transition(self, symbol: str) -> str:
        """δ(current_state, symbol) → next_state"""
        symbol_lower = symbol.strip().lower()
        table = TRANSITION_TABLE.get(self.current_state, {})

        if symbol_lower in table:
            next_state = table[symbol_lower]
        else:
            next_state = table.get("*", self.current_state)

        self.current_state = next_state
        self.history.append(next_state)
        return next_state

    def is_accept(self) -> bool:
        return self.current_state in ACCEPT_STATES

    def is_reject(self) -> bool:
        return self.current_state == REJECT_STATE

    def reset(self):
        self.current_state = START_STATE
        self.temp_data = {}
        self.history = [START_STATE]

    def get_state(self) -> str:
        return self.current_state

    def store(self, key: str, value: str):
        self.temp_data[key] = value

    def get_stored(self, key: str, default: str = "") -> str:
        return self.temp_data.get(key, default)

    def clear_temp_data(self):
        """Reset data registrasi sementara — dipanggil setelah ACCEPT/REJECT."""
        self.temp_data = {}

    def get_transitions_for_viz(self) -> list[tuple[str, str, str]]:
        """
        Returns list of (from_state, to_state, label) untuk visualisasi.
        Hanya transisi non-wildcard + wildcard penting.
        """
        edges = []
        shown = {
            "START":                 [("*", "MENU_UTAMA")],
            "MENU_UTAMA":            [("1","REGISTRASI_NAMA"),("2","LIHAT_JADWAL"),
                                      ("3","CEK_TIKET"),("4","INFO_VENUE"),("5","FAQ")],
            "REGISTRASI_NAMA":       [("valid","REGISTRASI_EMAIL"),("invalid","REJECT")],
            "REGISTRASI_EMAIL":      [("valid","REGISTRASI_TELEPON"),("invalid","REJECT")],
            "REGISTRASI_TELEPON":    [("valid","REGISTRASI_TIKET"),("invalid","REJECT")],
            "REGISTRASI_TIKET":      [("1/2/3","REGISTRASI_KONFIRMASI")],
            "REGISTRASI_KONFIRMASI": [("ya","ACCEPT"),("tidak","MENU_UTAMA")],
            "LIHAT_JADWAL":          [("*","MENU_UTAMA")],
            "CEK_TIKET":             [("valid","ACCEPT"),("invalid","REJECT")],
            "INFO_VENUE":            [("*","MENU_UTAMA")],
            "FAQ":                   [("*","MENU_UTAMA")],
            "ACCEPT":                [("*","MENU_UTAMA")],
            "REJECT":                [("*","MENU_UTAMA")],
        }
        for src, transitions in shown.items():
            for label, dst in transitions:
                edges.append((src, dst, label))
        return edges
