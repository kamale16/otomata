"""
app.py — EventBot v2 (Redesign: Casual Modern / WhatsApp-style)
Mata Kuliah: Teori Bahasa dan Otomata
"""

import streamlit as st
import json
import random
import qrcode
import io
import base64
from pathlib import Path

from fsm import EventBotFSM
from validator import validate_email, validate_phone, validate_kode_tiket, validate_nama, get_pattern_info
from grammar import parse, intent_to_menu_choice, get_cfg_info

st.set_page_config(
    page_title="EventBot",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Force sidebar terbuka
st.markdown("""
<style>
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: flex !important; transform: none !important; min-width: 240px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    with open(Path(__file__).parent / "data" / "events.json", "r", encoding="utf-8") as f:
        return json.load(f)

DATA = load_data()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; }
section[data-testid="stSidebar"] { background: #f0f2f5 !important; }
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* Chat bubbles */
.bubble-bot {
    background: #ffffff;
    border-radius: 2px 14px 14px 14px;
    padding: 10px 13px;
    margin: 2px 0 6px 0;
    max-width: 82%;
    font-size: 0.875rem;
    line-height: 1.55;
    color: #111827;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    display: inline-block;
}
.bubble-user {
    background: #dcf8c6;
    border-radius: 14px 2px 14px 14px;
    padding: 10px 13px;
    margin: 2px 0 6px 0;
    max-width: 75%;
    font-size: 0.875rem;
    line-height: 1.55;
    color: #111827;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    display: inline-block;
    float: right;
    clear: both;
}
.bot-row { clear: both; display: flex; align-items: flex-end; gap: 7px; margin-bottom: 2px; }
.user-row { clear: both; display: flex; justify-content: flex-end; margin-bottom: 2px; }
.avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: #128C7E; color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0; margin-bottom: 2px;
}
.timestamp { font-size: 0.68rem; color: #8696a0; margin-left: 4px; align-self: flex-end; }
.timestamp.u { margin-right: 4px; }
.chat-date-divider {
    text-align: center;
    margin: 12px 0 8px;
    font-size: 0.72rem;
    color: #8696a0;
}
.chat-date-divider span {
    background: #e1e9ee;
    padding: 3px 10px;
    border-radius: 8px;
}

/* Input area */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: none !important;
    border-radius: 24px !important;
    padding: 10px 16px !important;
    font-size: 0.9rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    color: #111827 !important;
}
.stButton > button {
    background: #128C7E !important;
    border: none !important;
    border-radius: 50% !important;
    width: 42px !important; height: 42px !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    color: white !important;
    box-shadow: 0 2px 6px rgba(18,140,126,0.35) !important;
    min-width: unset !important;
}
.stButton > button:hover { background: #0e7b6f !important; }

/* Quick buttons */
.quick-chip {
    display: inline-block;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 18px;
    padding: 5px 13px;
    font-size: 0.8rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #374151;
    cursor: pointer;
    margin: 2px;
    white-space: nowrap;
    transition: all 0.15s;
}
.quick-chip:hover { background: #f0faf9; border-color: #128C7E; color: #128C7E; }

/* Override semua Streamlit button jadi pill */
.stButton > button {
    background: white !important;
    border: 1px solid #d1d5db !important;
    border-radius: 18px !important;
    color: #374151 !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    padding: 4px 12px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    box-shadow: none !important;
    min-height: 32px !important;
    height: 32px !important;
    line-height: 1 !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #f0faf9 !important;
    border-color: #128C7E !important;
    color: #128C7E !important;
}

/* Sidebar */
.sb-header {
    background: #128C7E;
    color: white;
    padding: 14px 16px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.sb-name { font-size: 1rem; font-weight: 600; }
.sb-status { font-size: 0.75rem; opacity: 0.85; margin-top: 1px; }
.sb-section { padding: 10px 14px 4px; font-size: 0.7rem; font-weight: 600; color: #8696a0; text-transform: uppercase; letter-spacing: 0.05em; }
.sb-card {
    margin: 3px 10px;
    background: white;
    border-radius: 10px;
    padding: 8px 11px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
}
.sb-card-title { font-size: 0.75rem; font-weight: 600; color: #374151; }
.sb-card-sub { font-size: 0.68rem; color: #6b7280; margin-top: 1px; }
.state-pill {
    display: inline-block;
    background: #e8f5e9;
    color: #1b5e20;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 4px;
    font-family: monospace;
}
.state-pill.reject { background: #fce4ec; color: #880e4f; }
.state-pill.accept { background: #e8f5e9; color: #1b5e20; }
.state-pill.menu   { background: #e3f2fd; color: #0d47a1; }
.regex-mono {
    font-family: monospace;
    font-size: 0.65rem;
    color: #047857;
    background: #ecfdf5;
    padding: 3px 6px;
    border-radius: 5px;
    display: block;
    margin-top: 3px;
    word-break: break-all;
    line-height: 1.4;
}
.cfg-mono {
    font-family: monospace;
    font-size: 0.68rem;
    color: #1e40af;
    background: #eff6ff;
    padding: 5px 8px;
    border-radius: 6px;
    line-height: 1.7;
    margin-top: 2px;
}
.history-chip {
    display: inline-block;
    background: #f3f4f6;
    border-radius: 5px;
    padding: 1px 6px;
    font-family: monospace;
    font-size: 0.62rem;
    color: #6b7280;
    margin: 1px;
}
.history-chip.active { background: #dcfce7; color: #166534; font-weight: 700; }

/* chat wrapper bg */
.chat-wrapper {
    background: #efeae2;
    background-image: url("data:image/svg+xml,%3Csvg width='52' height='52' viewBox='0 0 52 52' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h52v52H0z' fill='%23d4c9b8' fill-opacity='0.08'/%3E%3C/svg%3E");
    padding: 10px 16px;
    min-height: 440px;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "fsm" not in st.session_state:
    st.session_state.fsm = EventBotFSM()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "initialized" not in st.session_state:
    st.session_state.initialized = False

fsm: EventBotFSM = st.session_state.fsm

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def gen_kode(jenis):
    prefix = {"Reguler": "REG", "Mahasiswa": "MHS", "VIP": "VIP"}.get(jenis, "EVT")
    return f"EVT-{prefix}-{random.randint(1000,9999)}"

def gen_qr_base64(text: str) -> str:
    qr = qrcode.QRCode(version=2, box_size=6, border=3,
        error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#128C7E", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def get_menu_msg():
    return (
        "Pilih layanan:\n\n"
        "1️⃣  Registrasi Peserta\n"
        "2️⃣  Lihat Jadwal\n"
        "3️⃣  Cek Status Tiket\n"
        "4️⃣  Info Venue\n"
        "5️⃣  FAQ\n\n"
        "Ketik angka atau langsung perintah, misalnya *daftar* atau *lihat jadwal*"
    )

def get_jadwal_msg():
    msg = "📅 *Jadwal Konferensi*\n\n"
    for h in DATA["jadwal"]:
        msg += f"*{h['hari']}*\n"
        for s in h["sesi"]:
            msg += f"  `{s['waktu']}` {s['judul']}\n  _{s['speaker']}_ · {s['ruang']}\n\n"
    return msg + "Balas apa saja untuk kembali ke menu."

def get_venue_msg():
    v = DATA["venue"]
    return (
        f"🏛️ *{v['nama']}*\n\n"
        f"📍 {v['alamat']}\n\n"
        f"Fasilitas: {', '.join(v['fasilitas'])}\n\n"
        f"🚌 {v['transportasi']}\n\n"
        f"Balas apa saja untuk kembali ke menu."
    )

def get_faq_msg():
    msg = "❓ *FAQ*\n\n"
    for i, f in enumerate(DATA["faq"], 1):
        msg += f"*{i}. {f['q']}*\n{f['a']}\n\n"
    return msg + "Balas apa saja untuk kembali ke menu."

def bot_response(user_input):
    state = fsm.get_state()
    ui = user_input.strip().lower()

    if state == "START":
        fsm.transition("*")
        e = DATA["event"]
        return (
            f"Halo! 👋 Selamat datang di *EventBot*\n\n"
            f"🎪 *{e['nama']}*\n"
            f"📅 {e['tanggal']} · 📍 {e['kota']}\n\n"
            + get_menu_msg()
        )

    if state == "MENU_UTAMA":
        parsed = parse(user_input)
        if parsed["matched"]:
            choice = intent_to_menu_choice(parsed["intent"])
            if choice:
                ui = choice
        if ui == "1":
            fsm.transition("1")
            return "Oke, mulai daftar! 📝\n\nLangkah *1/4* — Nama lengkap kamu siapa?"
        elif ui == "2":
            fsm.transition("2")
            resp = get_jadwal_msg()
            fsm.transition("*")
            return resp
        elif ui == "3":
            fsm.transition("3")
            return "Kirim *kode tiket* kamu yuk\n\nFormatnya: `EVT-XXX-1234`"
        elif ui == "4":
            fsm.transition("4")
            resp = get_venue_msg()
            fsm.transition("*")
            return resp
        elif ui == "5":
            fsm.transition("5")
            resp = get_faq_msg()
            fsm.transition("*")
            return resp
        else:
            return f"Hmm, nggak ngerti yang itu 😅\n\n{get_menu_msg()}"

    if state in ["REGISTRASI_NAMA","REGISTRASI_EMAIL","REGISTRASI_TELEPON",
                  "REGISTRASI_TIKET","REGISTRASI_KONFIRMASI"]:
        if ui in ["menu","kembali"]:
            fsm.reset()
            return f"Registrasi dibatalkan.\n\n{get_menu_msg()}"

    if state == "REGISTRASI_NAMA":
        ok, msg = validate_nama(user_input)
        if ok:
            fsm.store("nama", user_input.strip())
            fsm.transition("valid_nama")
            return f"Hai *{user_input.strip()}*! 👋\n\nLangkah *2/4* — Email kamu apa?"
        else:
            fsm.transition("*")
            return f"Ups, nama nggak valid nih 😅\n{msg}\n\nCoba lagi ya — nama lengkap kamu siapa?"

    if state == "REGISTRASI_EMAIL":
        ok, msg = validate_email(user_input)
        if ok:
            fsm.store("email", user_input.strip())
            fsm.transition("valid_email")
            return f"✅ Email tersimpan!\n\nLangkah *3/4* — Nomor HP aktif kamu? (format: 08xx...)"
        else:
            fsm.transition("*")   # loop di REGISTRASI_EMAIL
            return f"Email-nya salah format nih 😬\n\nContoh yang bener: `nama@email.com`\n\nCoba lagi — email kamu apa?"

    if state == "REGISTRASI_TELEPON":
        ok, msg = validate_phone(user_input)
        if ok:
            fsm.store("telepon", user_input.strip())
            fsm.transition("valid_phone")
            tikets = DATA["tiket"]
            resp = "Langkah *4/4* — Pilih tiket:\n\n"
            for i, t in enumerate(tikets, 1):
                resp += f"*{i}. {t['jenis']}* — {t['harga']}\n_{t['fasilitas']}_\n\n"
            resp += "Balas *1*, *2*, atau *3*"
            return resp
        else:
            fsm.transition("*")   # loop di REGISTRASI_TELEPON
            return f"Nomor HP-nya kurang tepat 😬\n\nFormat: `08xxxxxxxxxx` (10–13 digit)\n\nCoba lagi — nomor HP kamu?"

    if state == "REGISTRASI_TIKET":
        tikets = DATA["tiket"]
        if ui in ["1","2","3"]:
            t = tikets[int(ui)-1]
            fsm.store("tiket", t["jenis"])
            fsm.store("harga", t["harga"])
            fsm.transition(ui)
            nama  = fsm.get_stored("nama")
            email = fsm.get_stored("email")
            telp  = fsm.get_stored("telepon")
            return (
                f"Cek dulu ya sebelum konfirmasi 👀\n\n"
                f"👤 Nama: *{nama}*\n"
                f"📧 Email: {email}\n"
                f"📱 HP: {telp}\n"
                f"🎫 Tiket: *{t['jenis']}* — {t['harga']}\n\n"
                f"Sudah bener? Balas *ya* atau *tidak*"
            )
        else:
            fsm.transition("*")
            return "Pilihannya 1, 2, atau 3 aja ya 😄"

    if state == "REGISTRASI_KONFIRMASI":
        if ui in ["ya","yes","iya","y","bener","benar","oke","ok"]:
            fsm.transition("ya")
            kode  = gen_kode(fsm.get_stored("tiket"))
            jenis = fsm.get_stored("tiket")
            nama  = fsm.get_stored("nama")
            email = fsm.get_stored("email")
            fsm.clear_temp_data()
            # Simpan info QR ke session state untuk dirender langsung
            if "qr_pending" not in st.session_state:
                st.session_state.qr_pending = []
            st.session_state.qr_pending.append({
                "kode": kode, "nama": nama, "jenis": jenis, "email": email
            })
            return f"Pendaftaran berhasil! 🎉\n\nKode tiket kamu: `{kode}`\nNama: {nama} · {jenis}\nEmail: {email}\n\n_QR Code ditampilkan di bawah_"
        elif ui in ["tidak","nggak","gak","no","batal"]:
            fsm.transition("tidak")
            fsm.clear_temp_data()
            return f"Oke, dibatalin ya 🙏\n\n{get_menu_msg()}"
        else:
            fsm.transition("*")
            return "Balas *ya* kalau datanya udah bener, atau *tidak* kalau mau batal 😊"

    if state == "CEK_TIKET":
        # jika user ketik menu atau klik chip lain, balik ke menu
        if ui in ["menu", "kembali", "1", "2", "3", "4", "5",
                  "daftar", "jadwal", "venue", "faq", "cek tiket",
                  "📝 daftar", "📅 jadwal", "🎫 cek tiket", "🏛 venue", "❓ faq"]:
            fsm.transition("*")  # → MENU_UTAMA
            return get_menu_msg()
        ok, msg = validate_kode_tiket(user_input)
        if ok:
            kode = user_input.strip().upper()
            db = DATA.get("tiket_terdaftar", [])
            found = next((t for t in db if t["kode"] == kode), None)
            fsm.transition("valid_kode")
            if found:
                icon = "✅" if found["status"] == "Aktif" else "❌"
                return (
                    f"Ketemu! 🎫\n\n"
                    f"Kode: `{found['kode']}`\n"
                    f"Nama: *{found['nama']}*\n"
                    f"Tiket: {found['jenis']}\n"
                    f"Status: {icon} *{found['status']}*\n\n"
                    f"Ada yang lain?"
                )
            else:
                return f"Format kode valid, tapi nggak ada di database nih 🤔\n\nPastiin kodenya bener ya.\n\nAda yang lain?"
        else:
            fsm.transition("invalid")
            return f"Format kode-nya salah nih\n\nHarus kayak gini: `EVT-ABC-1234`\n\nKetik *menu* buat balik."

    if state == "ACCEPT":
        fsm.transition("*")
        return get_menu_msg()

    if state == "REJECT":
        fsm.transition("*")
        return f"Balik ke menu dulu ya 😊\n\n{get_menu_msg()}"

    fsm.transition("*")
    return get_menu_msg()


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Header
    st.markdown(f"""
    <div class="sb-header">
        <div style="display:flex;align-items:center;gap:10px">
            <div style="width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,0.25);
                display:flex;align-items:center;justify-content:center;font-size:18px">🎟️</div>
            <div>
                <div class="sb-name">EventBot</div>
                <div class="sb-status">● online — siap membantu</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    event = DATA["event"]
    venue = DATA["venue"]

    # Info Event
    st.markdown('<div class="sb-section">Info Event</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-card">
        <div class="sb-card-title">{event['nama']}</div>
        <div class="sb-card-sub" style="margin-top:5px">📅 {event['tanggal']}</div>
        <div class="sb-card-sub">📍 {venue['nama']}</div>
        <div class="sb-card-sub">🏙️ {event['kota']}</div>
        <div class="sb-card-sub" style="margin-top:4px">🎯 {event['tema']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Tiket
    st.markdown('<div class="sb-section">Tiket Tersedia</div>', unsafe_allow_html=True)
    for t in DATA["tiket"]:
        st.markdown(f"""
        <div class="sb-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div class="sb-card-title">{t['jenis']}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#128C7E">{t['harga']}</div>
            </div>
            <div class="sb-card-sub">{t['fasilitas']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Panduan
    st.markdown('<div class="sb-section">Cara Pakai</div>', unsafe_allow_html=True)
    panduan = [
        ("1️⃣", "Pilih menu 1–5 atau ketik perintah"),
        ("2️⃣", "Ikuti langkah registrasi"),
        ("3️⃣", "Simpan kode tiket kamu"),
    ]
    for icon, teks in panduan:
        st.markdown(f"""
        <div style="display:flex;gap:8px;align-items:flex-start;padding:4px 10px">
            <span style="font-size:0.8rem">{icon}</span>
            <span style="font-size:0.72rem;color:#374151;line-height:1.4">{teks}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #6b7280 !important;
        font-size: 0.75rem !important;
        font-weight: 400 !important;
        box-shadow: none !important;
        padding: 5px 10px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-height: 32px !important;
        height: 32px !important;
        line-height: 1 !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        border-color: #128C7E !important;
        color: #128C7E !important;
        background: #f0faf9 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("↺ Reset", use_container_width=True):
        fsm.reset()
        st.session_state.messages = []
        st.session_state.initialized = False
        st.rerun()
    st.markdown('<div style="text-align:center;font-size:0.7rem;color:#9ca3af;padding:6px 0">TBO 2025 · DFA + Regex + CFG</div>', unsafe_allow_html=True)


# ─── MAIN AREA ─────────────────────────────────────────────────────────────────
# Top bar
st.markdown("""
<div style="background:#128C7E;padding:11px 18px;display:flex;align-items:center;gap:11px">
    <div style="width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.22);
        display:flex;align-items:center;justify-content:center;font-size:17px">🎟️</div>
    <div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;color:white;font-size:0.95rem">EventBot</div>
        <div style="font-size:0.72rem;color:rgba(255,255,255,0.8)">Asisten pendaftaran konferensi TBO</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Init
if not st.session_state.initialized:
    add_message("assistant", bot_response("mulai"))
    st.session_state.initialized = True

# Chat messages
chat_html = '<div class="chat-wrapper">'
chat_html += '<div class="chat-date-divider"><span>Hari ini</span></div>'

import datetime
now = datetime.datetime.now()
for i, msg in enumerate(st.session_state.messages):
    t = (now - datetime.timedelta(minutes=len(st.session_state.messages)-i)).strftime("%H:%M")
    content = msg["content"].replace("\n", "<br>").replace("*", "<b>", 1)
    # proper bold: replace paired *text* with <b>text</b>
    import re
    display = re.sub(r'\*([^*]+)\*', r'<b>\1</b>', msg["content"].replace("\n", "<br>"))
    display = re.sub(r'`([^`]+)`', r'<code style="background:#f0fdf4;border-radius:4px;padding:1px 5px;font-family:monospace;font-size:0.82em;color:#065f46">\1</code>', display)
    display = re.sub(r'_([^_]+)_', r'<i>\1</i>', display)

    if msg["role"] == "assistant":
        if msg.get("is_html"):
            chat_html += f'''<div class="bot-row">
            <div class="avatar">🤖</div>
            <div class="bubble-bot">{msg["content"]}</div>
            <span class="timestamp">{t}</span>
        </div>'''
        else:
            chat_html += f'''<div class="bot-row">
            <div class="avatar">🤖</div>
            <div class="bubble-bot">{display}</div>
            <span class="timestamp">{t}</span>
        </div>'''
    else:
        chat_html += f'''<div class="user-row">
            <span class="timestamp u">{t}</span>
            <div class="bubble-user">{display}</div>
        </div>'''

chat_html += '<div style="clear:both"></div></div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Render QR code jika ada
if "qr_pending" in st.session_state and st.session_state.qr_pending:
    for qr_data in st.session_state.qr_pending:
        import qrcode, io
        qr = qrcode.QRCode(version=2, box_size=6, border=3,
            error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(qr_data["kode"])
        qr.make(fit=True)
        img = qr.make_image(fill_color="#128C7E", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.image(buf, width=200, caption=f"{qr_data['kode']} · {qr_data['nama']}")
    st.session_state.qr_pending = []

# Quick chips
st.markdown("""
<div style="background:#f0f2f5;padding:7px 14px;display:flex;flex-wrap:wrap;gap:5px;border-top:1px solid #e5e7eb">
""", unsafe_allow_html=True)

cols = st.columns(5)
chips = [("📝 Daftar","1"),("📅 Jadwal","2"),("🎫 Cek Tiket","3"),("🏛️ Venue","4"),("❓ FAQ","5")]
for col, (label, val) in zip(cols, chips):
    with col:
        if st.button(label, key=f"q_{val}", use_container_width=True):
            # reset FSM ke MENU_UTAMA dulu jika bukan state registrasi
            cur = fsm.get_state()
            if cur not in ["REGISTRASI_NAMA","REGISTRASI_EMAIL","REGISTRASI_TELEPON",
                           "REGISTRASI_TIKET","REGISTRASI_KONFIRMASI"]:
                if cur != "MENU_UTAMA":
                    fsm.current_state = "MENU_UTAMA"
            add_message("user", label)
            add_message("assistant", bot_response(val))
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Input
with st.form("chat_form", clear_on_submit=True):
    c1, c2 = st.columns([8, 1])
    with c1:
        user_input = st.text_input(
            "msg", placeholder="Ketik pesan...",
            label_visibility="collapsed"
        )
    with c2:
        sent = st.form_submit_button("➤")
    if sent and user_input.strip():
        add_message("user", user_input)
        add_message("assistant", bot_response(user_input))
        st.rerun()