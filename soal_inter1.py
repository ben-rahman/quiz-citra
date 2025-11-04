import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import io
from datetime import datetime

# -------------------------------
# AUTO REFRESH SETIAP 1 DETIK (agar timer realtime)
# -------------------------------
st_autorefresh(interval=1000, key="timer_refresh")

# -------------------------------
# KONFIGURASI SOAL
# -------------------------------
SOAL_TEORI = [
    "1. Jelaskan apa yang dimaksud dengan transformasi geometri pada citra digital!",
    "2. Apa fungsi dari matriks transformasi dalam operasi translasi, rotasi, dan skala?",
    "3. Sebutkan perbedaan antara rotasi dan transformasi perspektif!",
    "4. Apa tujuan dari transformasi skala (scaling) dalam pengolahan citra digital?",
    "5. Dalam konteks DUDI, sebutkan satu contoh penerapan transformasi perspektif di industri nyata!"
]

SOAL_ESSAY = [
    """6. Jelaskan secara rinci bagaimana proses rotasi citra bekerja di OpenCV!
Dalam penjelasanmu, sertakan:
- Fungsi Python yang digunakan,
- Penjelasan parameter (pusat rotasi, sudut, skala),
- Dampak visual dari perubahan sudut.""",
    """7. Bandingkan dan jelaskan perbedaan antara transformasi afine dan transformasi perspektif.
Sertakan contoh aplikasinya dalam industri!"""
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
st.markdown("<h1 style='text-align:center; color:#0066cc;'>🧠 QUIZ - PENGOLAHAN CITRA DIGITAL</h1>", unsafe_allow_html=True)
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
    durasi_per_soal = 3  # contoh: 30 detik per soal teori
    soal_list = SOAL_TEORI
elif st.session_state.phase == "essay":
    durasi_per_soal = 6  # contoh: 60 detik per soal essay
    soal_list = SOAL_ESSAY
else:
    soal_list = []
    durasi_per_soal = 0

# -------------------------------
# LOGIKA PENAMPILAN SOAL
# -------------------------------
soal_index = int(elapsed // durasi_per_soal)
sisa_waktu = int(durasi_per_soal - (elapsed % durasi_per_soal))
progress = max(0.0, 1 - (sisa_waktu / durasi_per_soal))

if soal_index >= len(soal_list):
    if st.session_state.phase == "teori":
        st.session_state.phase = "essay"
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        # -------------------------------
        # UJIAN SELESAI
        # -------------------------------
        st.success("🎉 Ujian selesai! Terima kasih telah mengerjakan.")
        df = pd.DataFrame(list(st.session_state.answers.items()), columns=["Soal", "Jawaban"])
        filename = f"Jawaban_{st.session_state.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇️ Download Jawaban Saya (CSV)",
            data=csv_buffer.getvalue(),
            file_name=filename,
            mime="text/csv"
        )

        st.info("📤 Setelah download, kirim file CSV ke dosen melalui link atau email yang disediakan.")
        st.warning("⚠️ Jika tombol download tidak berfungsi, salin teks di bawah ini dan kirimkan lewat form resmi.")
        for s, j in st.session_state.answers.items():
            st.text(f"{s}:\n{j}\n")
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
    st.metric("⏳ Sisa Waktu", f"{sisa_waktu} detik")

# -------------------------------
# INPUT JAWABAN (AMAN)
# -------------------------------
key_soal = f"{fase_nama} {soal_index+1}"
existing_answer = st.session_state.answers.get(key_soal, "")
jawaban = st.text_area("✏️ Jawaban Anda:", value=existing_answer, key=f"input_{key_soal}", height=200)
if jawaban.strip() != existing_answer:
    st.session_state.answers[key_soal] = jawaban

st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Ujian Digital | Dibuat oleh Dr. Benrahman 😎</p>", unsafe_allow_html=True)

