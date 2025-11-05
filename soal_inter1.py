import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
from datetime import datetime

# -------------------------------
# AUTO REFRESH SETIAP 1 DETIK
# -------------------------------
st_autorefresh(interval=1000, key="timer_refresh")  # auto rerun tiap 1 detik

# -------------------------------
# KONFIGURASI SOAL - BLOCKCHAIN & BUSINESS MANAGEMENT
# -------------------------------
SOAL_TEORI = [
    "1. Jelaskan secara singkat apa yang dimaksud dengan Blockchain dan bagaimana perbedaannya dengan database tradisional.",
    "2. Apa peran dari hash function dalam sistem Blockchain, dan mengapa sifat 'immutability' penting?",
    "3. Sebutkan dan jelaskan secara singkat tiga komponen utama dalam blok Blockchain.",
    "4. Apa yang dimaksud dengan mekanisme konsensus, dan berikan dua contoh jenis mekanisme konsensus yang populer.",
    "5. Mengapa desentralisasi dianggap sebagai salah satu keunggulan utama Blockchain dibandingkan sistem terpusat?"
]

SOAL_ESSAY = [
    """6. Jelaskan secara mendalam bagaimana proses mining bekerja pada Blockchain berbasis Proof of Work (PoW).
Dalam penjelasanmu, sertakan:
- Langkah-langkah utama dari pembentukan blok hingga validasi transaksi,
- Peran node dan miner,
- Dampak efisiensi energi serta alternatif yang lebih berkelanjutan.""",
    """7. Analisis bagaimana smart contract pada platform seperti Ethereum mengubah paradigma transaksi digital.
Jelaskan konsep dasar, manfaat, serta risiko yang muncul (termasuk bug dan implikasi kepercayaan sistem)."""
]

# -------------------------------
# STATE
# -------------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "phase" not in st.session_state:
    st.session_state.phase = "teori"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "name" not in st.session_state:
    st.session_state.name = ""

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center; color:#0066cc;'>🧠 QUIZ - BLOCKCHAIN & BUSINESS MANAGEMENT</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# LOGIN DAN MULAI
# -------------------------------
if st.session_state.start_time is None:
    st.session_state.name = st.text_input("Masukkan Nama Lengkap Anda:")
    if st.button("🚀 Mulai Ujian"):
        if not st.session_state.name.strip():
            st.warning("Masukkan nama dulu bro 😅")
        else:
            st.session_state.start_time = time.time()
            st.session_state.phase = "teori"
            st.session_state.current_index = 0
            st.rerun()
    st.stop()

# -------------------------------
# TIMER DAN FASE
# -------------------------------
elapsed = time.time() - st.session_state.start_time

if st.session_state.phase == "teori":
    durasi_per_soal = 90  # 3 menit per soal teori
    soal_list = SOAL_TEORI
elif st.session_state.phase == "essay":
    durasi_per_soal = 450  # 15 menit per soal essay
    soal_list = SOAL_ESSAY
else:
    soal_list = []
    durasi_per_soal = 0

# -------------------------------
# LOGIKA PENAMPILAN SOAL
# -------------------------------
soal_index = int(elapsed // durasi_per_soal)
sisa_waktu = durasi_per_soal - (elapsed % durasi_per_soal)
progress = max(0.0, 1 - (sisa_waktu / durasi_per_soal))

if soal_index >= len(soal_list):
    if st.session_state.phase == "teori":
        st.session_state.phase = "essay"
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        st.success("🎉 Ujian selesai! Terima kasih telah mengerjakan.")
        df = pd.DataFrame(list(st.session_state.answers.items()), columns=["Soal", "Jawaban"])
        filename = f"Jawaban_Blockchain_{st.session_state.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        st.write(f"📁 Jawaban disimpan otomatis ke: `{filename}`")
        st.stop()

# -------------------------------
# TAMPILKAN SOAL AKTIF
# -------------------------------
soal = soal_list[soal_index]
fase_nama = "🧩 Soal Teori" if st.session_state.phase == "teori" else "📝 Soal Essay"

st.markdown(f"### {fase_nama} #{soal_index + 1}")
st.info(soal)

# Progress Bar & Timer
col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress)
with col2:
    st.metric("⏳ Sisa Waktu", f"{int(sisa_waktu)} detik")

# -------------------------------
# INPUT JAWABAN
# -------------------------------
jawaban = st.text_area("✏️ Jawaban Anda:", 
                       key=f"jawaban_{st.session_state.phase}_{soal_index}",
                       height=200)
st.session_state.answers[f"{fase_nama} {soal_index+1}"] = jawaban

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Ujian Digital Blockchain | Dibuat oleh Dr.Benrahman 😎</p>", unsafe_allow_html=True)

