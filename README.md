# 🎪 EventBot v2 — Chatbot Manajemen Konferensi

> **Mata Kuliah:** Teori Bahasa dan Otomata  
> **Tema:** Manajemen Event & Konferensi  
> **Konsep TBO:** DFA/FSM + Regular Expression + Context-Free Grammar + Visualisasi

---

## 📁 Struktur Project

```
eventbot/
├── app.py           ← Main Streamlit app
├── fsm.py           ← Finite State Machine (DFA engine)
├── validator.py     ← Regex validation (Regular Language)
├── grammar.py       ← CFG parser + Stemming BI
├── visualizer.py    ← Diagram FSM dengan Graphviz
├── requirements.txt
└── data/
    └── events.json  ← Data event, jadwal, tiket
```

---

## 🚀 Cara Menjalankan

```bash
# Pastikan graphviz system terinstall:
# Ubuntu/Debian: sudo apt-get install graphviz
# macOS:         brew install graphviz
# Windows:       https://graphviz.org/download/

pip install -r requirements.txt
streamlit run app.py
```

Buka: **http://localhost:8501**

---

## ✅ Perbaikan dari v1

| # | Bug/Kekurangan v1 | Status v2 |
|---|-------------------|-----------|
| 1 | Folder `{data}` duplikat | ✅ Fix |
| 2 | State LIHAT_JADWAL/INFO_VENUE/FAQ tidak pernah aktif | ✅ Fix — semua state kini aktif |
| 3 | MENU_UTAMA tidak konsisten dengan GREETING | ✅ Fix — START langsung ke MENU_UTAMA |
| 4 | `temp_data` tidak di-reset setelah ACCEPT/REJECT | ✅ Fix — `clear_temp_data()` dipanggil |
| 5 | CEK_TIKET ke ACCEPT tanpa info cara kembali | ✅ Fix — pesan panduan jelas |
| 6 | CFG tidak mengenali imbuhan BI (`daftarkan`, `mengecek`) | ✅ Fix — Stemming BI ditambahkan |
| 7 | Pilihan tiket invalid tidak memberikan repeat prompt jelas | ✅ Fix — wildcard loop + pesan jelas |
| 8 | Tidak ada visualisasi diagram FSM | ✅ Fix — diagram SVG via Graphviz |
| 9 | CFG productions didefinisikan tapi tidak dipakai parsing | ✅ Fix — parser menggunakan CFG_PRODUCTIONS |

---

## 🧠 Konsep TBO

### DFA: M = (Q, Σ, δ, q0, F)

```
Q  = {START, MENU_UTAMA, REGISTRASI_NAMA, REGISTRASI_EMAIL,
      REGISTRASI_TELEPON, REGISTRASI_TIKET, REGISTRASI_KONFIRMASI,
      LIHAT_JADWAL, CEK_TIKET, INFO_VENUE, FAQ, ACCEPT, REJECT}

q0 = START
F  = {ACCEPT}
```

### Regular Language (Regex)

| Input | Pattern |
|-------|---------|
| Email | `^[\w\.\-\+]+@[\w\-]+\.[a-zA-Z]{2,}$` |
| HP | `^(?:\+62\|0)8[1-9][0-9]{7,10}$` |
| Kode Tiket | `^EVT-[A-Z]{3}-\d{4}$` |
| Nama | `^[A-Za-z\s\.\-]{3,60}$` |

### CFG (Tipe 2 Chomsky)

```
S  → VP NP | VP | NP
VP → daftar | lihat | cek | info | batal | ...
NP → event | tiket | jadwal | venue | faq
```

Dengan stemming Bahasa Indonesia:
- `daftarkan` → `daftar`
- `mengecek` → `cek`  
- `konferensi` → `event`
