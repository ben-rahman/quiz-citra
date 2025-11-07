import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
from datetime import datetime

# -------------------------------
# AUTO REFRESH SETIAP 1 DETIK
# -------------------------------
st_autorefresh(interval=1000, key="timer_refresh")

# -------------------------------
# KONFIGURASI SOAL - DATA MINING (Pertemuan 1–5)
# -------------------------------
SOAL_TEORI = [
    # Pertemuan 1
    "1. Jelaskan secara singkat apa yang dimaksud dengan Data Mining dan bagaimana perbedaannya dengan Machine Learning.",
    # Pertemuan 2
    "2. Sebutkan tiga komponen utama dalam arsitektur Data Warehouse beserta fungsinya.",
    # Pertemuan 3
    "3. Apa tujuan utama dari proses data cleaning dalam Data Preprocessing?",
    # Pertemuan 4
    "4. Jelaskan perbedaan antara Feature Selection dan Feature Engineering.",
    # Pertemuan 5
    "5. Sebutkan enam tahap utama dalam framework CRISP-DM dan urutan logisnya."
]

SOAL_ESSAY = [
    """6. Jelaskan bagaimana hubungan antara Data Warehouse, OLAP, dan Data Mining dalam mendukung proses pengambilan keputusan organisasi. Sertakan ilustrasi alur sederhana.""",
    """7. Berdasarkan pemahaman Anda terhadap CRISP-DM dan Data Preprocessing, jelaskan pentingnya integrasi antara Business Understanding, Data Preparation, dan Modeling agar hasil Data Mining dapat bermanfaat secara nyata. Sertakan contoh kasus sederhana."""
]

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
st.markdown("<h1 style='text-align:center; color:#0066cc;'>📊 QUIZ / TUGAS 1 – DATA MINING</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>Materi Pertemuan 1 s.d 5</h4>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# LOGIN DAN MULAI
# -------------------------------
if st.session_state.start_time is None:
    st.session_state.name = st.text_input("Masukkan Nama Lengkap Anda:")
    if st.button("🚀 Mulai Ujian / Tugas"):
        if not st.session_state.name.strip():
            st.warning("Masukkan nama dulu bro 😅")
        else:
            st.session_state.start_time = time.time()
            st.session_state.phase = "teori"
            st.session_state.current_index = 0
            st.rerun()
    st.stop()

# -------------------------------
# TENTUKAN FASE & DURASI PER SOAL
# -------------------------------
if st.session_state.phase == "teori":
    soal_list = SOAL_TEORI
    durasi_per_soal = 120  # 2 menit per soal teori (short answer)
elif st.session_state.phase == "essay":
    soal_list = SOAL_ESSAY
    durasi_per_soal = 420  # 7 menit per soal essay (long answer)
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
        st.success("🎉 Tugas selesai! Terima kasih telah mengerjakan semua soal.")
        st.stop()

# -------------------------------
# TAMPILKAN SOAL AKTIF
# -------------------------------
soal = soal_list[soal_index]
fase_nama = "🧩 Short Answer (Teori)" if st.session_state.phase == "teori" else "📝 Long Answer (Essay)"

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
    height=200 if st.session_state.phase == "teori" else 300
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

        # Pindah ke soal berikutnya
        st.session_state.current_index += 1
        st.session_state.start_time = time.time()
        time.sleep(1)
        st.rerun()

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Quiz / Tugas 1 – Data Mining | Dibuat oleh Dr. H. Benrahman 😎</p>", unsafe_allow_html=True)


