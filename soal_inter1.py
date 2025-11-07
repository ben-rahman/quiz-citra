import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
from datetime import datetime
import os

# -------------------------------
# AUTO REFRESH SETIAP 1 DETIK
# -------------------------------
st_autorefresh(interval=1000, key="timer_refresh")

# -------------------------------
# KONFIGURASI SOAL - DATA MINING (Pertemuan 1–5)
# -------------------------------
SOAL_TEORI = [
    "1. Jelaskan secara singkat apa yang dimaksud dengan Data Mining dan bagaimana perbedaannya dengan Machine Learning.",
    "2. Sebutkan tiga komponen utama dalam arsitektur Data Warehouse beserta fungsinya.",
    "3. Apa tujuan utama dari proses data cleaning dalam Data Preprocessing?",
    "4. Jelaskan perbedaan antara Feature Selection dan Feature Engineering.",
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
    durasi_per_soal = 120  # 2 menit per soal teori
elif st.session_state.phase == "essay":
    soal_list = SOAL_ESSAY
    durasi_per_soal = 420  # 7 menit per soal essay
else:
    soal_list = []
    durasi_per_soal = 0

soal_index = st.session_state.current_index

# -------------------------------
# SELESAI SEMUA SOAL
# -------------------------------
if soal_index >= len(soal_list):
    if st.session_state.phase == "teori":
        st.session_state.phase = "essay"
        st.session_state.current_index = 0
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        # -------------------------------
        # UJIAN SELESAI
        # -------------------------------
        st.success("🎉 Ujian / Tugas Selesai! Terima kasih telah mengerjakan semua soal.")

        # Gabungkan semua jawaban jadi satu file
        df_all = pd.DataFrame(list(st.session_state.answers.items()), columns=["Soal", "Jawaban"])
        filename_all = f"JawabanLengkap_{st.session_state.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_all.to_csv(filename_all, index=False, encoding="utf-8-sig")

        st.info("📁 Semua jawaban Anda telah tersimpan otomatis ke file berikut:")
        st.code(os.path.abspath(filename_all), language="bash")

        st.markdown("### 📤 Kirim Jawaban ke Dosen via WhatsApp")
        wa_message = f"""
Assalamu'alaikum Pak 🙏
Saya {st.session_state.name}.
Berikut file hasil ujian/tugas Data Mining saya.

Nama File:
📎 {filename_all}

Terima kasih, Pak. 🙏
        """.strip()
        st.text_area("Pesan Siap Kirim ke WA:", wa_message, height=180)
        st.markdown("📲 **Langkah:**")
        st.markdown("""
1. Buka folder di atas dan cari file **JawabanLengkap_NamaAnda.csv**  
2. Kirim file tersebut ke dosen via **WhatsApp** bersama pesan di atas  
3. Pastikan file sudah terkirim dengan benar ✅
        """)

        st.stop()

# -------------------------------
# TAMPILKAN SOAL AKTIF
# -------------------------------
soal = soal_list[soal]()_
