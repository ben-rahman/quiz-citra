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
# KONFIGURASI SOAL - ANALITIK & MANAJEMEN BIG DATA
# -------------------------------
SOAL_TEORI = [
    "1. Apa perbedaan antara variabel kategorikal dan variabel numerik dalam konteks analisis Big Data?",
    "2. Sebutkan dua metode yang dapat digunakan untuk mendeteksi missing values pada dataset.",
    "3. Mengapa statistik deskriptif penting sebelum melakukan analisis data lebih lanjut?",
    "4. Jelaskan secara singkat tujuan dari proses data cleaning dalam tahap preprocessing.",
    "5. Sebutkan enam tahapan utama dalam metodologi CRISP-DM."
]

SOAL_ESSAY = [
    """6. Jelaskan bagaimana hubungan antara proses data preprocessing (cleaning, transformation, integration) 
dengan kualitas hasil akhir dari data mining. Sertakan contoh kasus sederhana.""",
    """7. Menurut Anda, mengapa pemahaman terhadap alur kerja CRISP-DM sangat penting bagi seorang data scientist 
sebelum memulai proyek Big Data?"""
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
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center; color:#0066cc;'>🧠 QUIZ - ANALITIK & MANAJEMEN BIG DATA</h1>", unsafe_allow_html=True)
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
# TENTUKAN FASE DAN SOAL AKTIF
# -------------------------------
if st.session_state.phase == "teori":
    soal_list = SOAL_TEORI
    durasi_per_soal = 90
elif st.session_state.phase == "essay":
    soal_list = SOAL_ESSAY
    durasi_per_soal = 300
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
jawaban = st.text_area("✏️ Jawaban Anda:",
                       key=f"jawaban_{st.session_state.phase}_{soal_index}",
                       height=200)
st.session_state.answers[f"{fase_nama} {soal_index+1}"] = jawaban

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

        filename = f"Jawaban_{st.session_state.name}_soal{soal_index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        st.success(f"✅ Jawaban soal {soal_index+1} disimpan otomatis ke `{filename}`")

        # Pindah ke soal berikutnya
        st.session_state.current_index += 1
        st.session_state.start_time = time.time()
        time.sleep(1)
        st.rerun()

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Ujian Digital Analitik & Manajemen Big Data | Dibuat oleh Dr. H. Benrahman 😎</p>", unsafe_allow_html=True)


