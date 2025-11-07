import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
from datetime import datetime
import io

# -------------------------------
# AUTO REFRESH SETIAP 1 DETIK
# -------------------------------
st_autorefresh(interval=1000, key="timer_refresh")

# -------------------------------
# KONFIGURASI SOAL
# -------------------------------
SOAL_TEORI = [
    "1. Jelaskan secara singkat apa yang dimaksud dengan Data Mining dan bagaimana perbedaannya dengan Machine Learning.",
    "2. Sebutkan tiga komponen utama dalam arsitektur Data Warehouse beserta fungsinya.",
    "3. Apa tujuan utama dari proses data cleaning dalam Data Preprocessing?",
    "4. Jelaskan perbedaan antara Feature Selection dan Feature Engineering.",
    "5. Sebutkan enam tahap utama dalam framework CRISP-DM dan urutan logisnya."
]

SOAL_ESSAY = [
    """6. Jelaskan bagaimana hubungan antara Data Warehouse, OLAP, dan Data Mining dalam mendukung proses pengambilan keputusan organisasi.""",
    """7. Berdasarkan pemahaman Anda terhadap CRISP-DM dan Data Preprocessing, jelaskan pentingnya integrasi antara Business Understanding, Data Preparation, dan Modeling."""
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
st.markdown("<h1 style='text-align:center; color:#0066cc;'>📊 QUIZ / TUGAS 1 – DATA MINING</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>Materi Pertemuan 1 s.d 5</h4>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# LOGIN
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
# PILIH FASE DAN SOAL
# -------------------------------
if st.session_state.phase == "teori":
    soal_list = SOAL_TEORI
    durasi_per_soal = 120
elif st.session_state.phase == "essay":
    soal_list = SOAL_ESSAY
    durasi_per_soal = 420
else:
    soal_list = []
    durasi_per_soal = 0

soal_index = st.session_state.current_index

# -------------------------------
# JIKA SUDAH SELESAI SEMUA SOAL
# -------------------------------
if soal_index >= len(soal_list):
    if st.session_state.phase == "teori":
        # Lanjut ke essay
        st.session_state.phase = "essay"
        st.session_state.current_index = 0
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        # Semua fase selesai ✅
        st.success("🎉 Ujian / Tugas Selesai! Terima kasih telah mengerjakan semua soal.")

        df_all = pd.DataFrame(list(st.session_state.answers.items()), columns=["Soal", "Jawaban"])
        filename_all = f"JawabanLengkap_{st.session_state.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        csv_buffer = io.StringIO()
        df_all.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_data = csv_buffer.getvalue()

        st.markdown("### 📥 Unduh Hasil Jawaban Anda")
        st.download_button(
            label="⬇️ Download File Jawaban Saya (CSV)",
            data=csv_data,
            file_name=filename_all,
            mime="text/csv"
        )

        st.markdown("### 📤 Kirim File ke Dosen via WhatsApp")
        wa_message = f"""
Assalamu'alaikum Pak 🙏  
Saya {st.session_state.name}.  
Berikut file hasil ujian/tugas Data Mining saya.  

Nama File:  
📎 {filename_all}  

Terima kasih, Pak 🙏
        """.strip()
        st.text_area("Pesan Siap Kirim:", wa_message, height=150)
        st.stop()

# -------------------------------
# TAMPILKAN SOAL AKTIF
# -------------------------------
soal = soal_list[soal_index]
fase_nama = "🧩 Short Answer (Teori)" if st.session_state.phase == "teori" else "📝 Long Answer (Essay)"

st.markdown(f"### {fase_nama} #{soal_index + 1}")
st.info(soal)

# -------------------------------
# TIMER
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
jawaban = st.text_area("✏️ Jawaban Anda:", key=f"jawaban_{st.session_state.phase}_{soal_index}", height=250)
st.session_state.answers[f"{fase_nama} {soal_index + 1}"] = jawaban

# -------------------------------
# LANJUT KE SOAL BERIKUTNYA
# -------------------------------
if st.button("➡️ Lanjut ke Soal Berikutnya"):
    if not jawaban.strip():
        st.warning("Isi dulu jawabannya bro 😅")
    else:
        st.session_state.current_index += 1
        st.session_state.start_time = time.time()
        time.sleep(0.5)
        st.rerun()

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Ujian Digital Data Mining | Dr. H. Benrahman 😎</p>", unsafe_allow_html=True)
