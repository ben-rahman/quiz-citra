import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
from datetime import datetime

# -------------------------------
# AUTO REFRESH SETIAP 1 DETIK (realtime timer)
# -------------------------------
st_autorefresh(interval=1000, key="timer_refresh")

# -------------------------------
# KONFIGURASI SOAL - SIMULASI DAN PEMODELAN
# -------------------------------
SOAL_TEORI = [
    "1. Apa yang dimaksud dengan simulasi dalam konteks sistem dinamis?",
    "2. Sebutkan tiga jenis model dalam pemodelan sistem!",
    "3. Apa perbedaan antara model deterministik dan stokastik?",
    "4. Mengapa validasi model penting dalam simulasi?",
    "5. Apa tujuan utama dari verifikasi dalam pemodelan simulasi?"
]

SOAL_ESSAY = [
    """6. Jelaskan langkah-langkah umum dalam proses pemodelan dan simulasi sistem!""",
    """7. Jelaskan peran simulasi dalam pengambilan keputusan di dunia nyata, sertakan contoh aplikasinya!"""
]

# -------------------------------
# KONFIGURASI JAM MULAI (opsional)
# -------------------------------
WAKTU_MULAI = "13:30"

# -------------------------------
# STATE MANAGEMENT
# -------------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "phase" not in st.session_state:
    st.session_state.phase = "teori"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "name" not in st.session_state:
    st.session_state.name = ""
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center; color:#0066cc;'>🧮 QUIZ - SIMULASI DAN PEMODELAN</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# CEK WAKTU MULAI OTOMATIS
# -------------------------------
now = datetime.now().strftime("%H:%M")
if now < WAKTU_MULAI:
    st.warning(f"⏰ Ujian akan dimulai otomatis pada pukul **{WAKTU_MULAI}**. Sekarang pukul **{now}**.")
    st.stop()

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
# TENTUKAN FASE DAN SOAL AKTIF
# -------------------------------
if st.session_state.phase == "teori":
    soal_list = SOAL_TEORI
    durasi_per_soal = 180  # 3 menit per soal teori
elif st.session_state.phase == "essay":
    soal_list = SOAL_ESSAY
    durasi_per_soal = 900  # 15 menit per soal essay
else:
    soal_list = []
    durasi_per_soal = 0

soal_index = st.session_state.current_index
if soal_index >= len(soal_list):
    if st.session_state.phase == "teori":
        st.session_state.phase = "essay"
        st.session_state.current_index = 0
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        st.success("🎉 Ujian selesai! Terima kasih telah mengerjakan semua soal.")
        st.stop()

# -------------------------------
# TAMPILKAN SOAL AKTIF
# -------------------------------
soal = soal_list[soal_index]
fase_nama = "🧩 Soal Teori" if st.session_state.phase == "teori" else "📝 Soal Essay"

st.markdown(f"### {fase_nama} #{soal_index + 1}")
st.info(soal)

# -------------------------------
# TIMER & PROGRESS
# -------------------------------
elapsed = time.time() - st.session_state.start_time
sisa_waktu = durasi_per_soal - (elapsed % durasi_per_soal)
progress = max(0.0, 1 - (sisa_waktu / durasi_per_soal))

col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress)
with col2:
    st.metric("⏳ Sisa Waktu", f"{int(sisa_waktu)} detik")

# -------------------------------
# INPUT JAWABAN
# -------------------------------
jawaban = st.text_area(
    "✏️ Jawaban Anda:",
    key=f"jawaban_{st.session_state.phase}_{soal_index}",
    height=200
)
st.session_state.answers[f"{fase_nama} {soal_index + 1}"] = jawaban

# -------------------------------
# SAVE JAWABAN & TOMBOL LANJUT
# -------------------------------
if st.button("➡️ Lanjut ke Soal Berikutnya"):
    if not jawaban.strip():
        st.warning("Isi dulu jawabannya bro 😅")
    else:
        # Simpan ke file CSV per soal
        df = pd.DataFrame([{
            "Nama": st.session_state.name,
            "Fase": st.session_state.phase,
            "Nomor Soal": soal_index + 1,
            "Soal": soal,
            "Jawaban": jawaban,
            "Waktu Simpan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        filename = f"Jawaban_{st.session_state.name}_soal{soal_index + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        st.success(f"✅ Jawaban soal {soal_index + 1} disimpan otomatis ke `{filename}`")

        # Lanjut ke soal berikutnya
        st.session_state.current_index += 1
        st.session_state.start_time = time.time()
        time.sleep(1)
        st.rerun()

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Ujian Digital Simulasi & Pemodelan | Dibuat oleh Dr. H. Benrahman 😎</p>", unsafe_allow_html=True)


