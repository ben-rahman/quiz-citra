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
# KONFIGURASI SOAL PPS
# -------------------------------
SOAL_TEORI = [
    "1. Jelaskan secara kronologis pergeseran paradigma dalam Software Engineering mulai dari Waterfall Model hingga AI-Native Development. Sertakan alasan utama mengapa setiap paradigma muncul menggantikan sebelumnya.",
    "2. Bandingkan secara kritis antara Scrum dan Kanban dalam konteks efektivitas pengelolaan proyek dinamis. Berikan satu contoh kasus nyata di mana masing-masing metode lebih unggul dari yang lain.",
    "3. Uraikan konsep dasar Continuous Integration dan Continuous Deployment serta hubungannya dengan filosofi DevOps. Jelaskan pula dampaknya terhadap kecepatan dan kualitas pengiriman perangkat lunak modern.",
    "4. Bedakan antara Functional Requirements dan Non-Functional Requirements. Jelaskan dengan contoh dari sistem reservasi rumah sakit yang telah Anda pelajari pada sesi hands-on.",
    "5. Apa yang dimaksud dengan wicked problems dalam pengembangan perangkat lunak berskala besar? Jelaskan bagaimana integrasi teknologi AI, IoT, dan Big Data memperumit proses rekayasa perangkat lunak."
]

SOAL_ESSAY = [
    """6. Misalkan Anda menjadi Project Manager untuk proyek pengembangan aplikasi e-commerce nasional. 
Buat analisis komprehensif mengenai bagaimana timeline, risiko, dan output proyek akan berbeda jika dijalankan 
dengan pendekatan Waterfall dibandingkan Agile Scrum. Sertakan rancangan mini-SDLC plan untuk masing-masing 
pendekatan dan jelaskan mengapa salah satunya lebih cocok untuk konteks proyek tersebut.""",

    """7. Analisis sebuah kasus nyata atau hipotetis kegagalan proyek software pemerintah (misalnya sistem pajak digital, 
e-KTP, atau sistem bansos). Identifikasi elemen wicked problem-nya, kesalahan pada tahapan requirement engineering, 
dan potensi perbaikan jika prinsip DevOps, AI-driven analytics, dan CI/CD pipeline diterapkan. 
Buat diagram cause–effect (Ishikawa/Fishbone) untuk mendukung penjelasan Anda."""
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
st.markdown("<h1 style='text-align:center; color:#0066cc;'>QUIZ / TUGAS 1 - PPS – SOFTWARE ENGINEERING</h1>", unsafe_allow_html=True)
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
            st.session_state.answers = {}
            st.rerun()
    st.stop()

# -------------------------------
# PILIH FASE DAN SOAL
# -------------------------------
if st.session_state.phase == "teori":
    soal_list = SOAL_TEORI
    durasi_per_soal = 180  # 3 menit per soal
elif st.session_state.phase == "essay":
    soal_list = SOAL_ESSAY
    durasi_per_soal = 600  # 10 menit per soal
else:
    soal_list = []
    durasi_per_soal = 0

soal_index = st.session_state.current_index

# -------------------------------
# CEK APAKAH SEMUA SOAL SUDAH SELESAI
# -------------------------------
if soal_index >= len(soal_list):
    if st.session_state.phase == "teori":
        # Lanjut ke bagian essay
        st.session_state.phase = "essay"
        st.session_state.current_index = 0
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        # SEMUA SUDAH SELESAI ✅
        st.success("🎉 Ujian / Tugas Selesai! Terima kasih telah mengerjakan semua soal.")

        # Buat DataFrame berisi semua jawaban
        df_all = pd.DataFrame(list(st.session_state.answers.items()), columns=["Soal", "Jawaban"])
        filename_all = f"Jawaban_PPS_{st.session_state.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        csv_bytes = io.BytesIO()
        df_all.to_csv(csv_bytes, index=False, encoding="utf-8-sig")
        csv_bytes.seek(0)

        st.markdown("### 📥 Unduh Hasil Jawaban Anda")
        st.download_button(
            label="⬇️ Download File Jawaban Saya (CSV)",
            data=csv_bytes,
            file_name=filename_all,
            mime="text/csv"
        )

        st.markdown("### 📤 Kirim File ke Dosen via WhatsApp")
        wa_message = f"""
Assalamu'alaikum Pak 🙏  
Saya *{st.session_state.name}*.  
Berikut file hasil ujian/tugas PPS saya.  

Nama File:  
📎 {filename_all}  

Terima kasih, Pak 🙏
        """.strip()

        st.text_area("Pesan Siap Kirim ke WA:", wa_message, height=250)

        st.markdown("""
📲 **Langkah-langkah:**
1. Klik tombol **Download File Jawaban Saya (CSV)** di atas.  
2. File akan tersimpan di **folder Downloads** perangkat Anda.  
3. Kirim file CSV tersebut ke dosen via **WhatsApp** beserta pesan di atas.  
4. Pastikan file terkirim dengan benar ✅  
        """)

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
jawaban = st.text_area(
    "✏️ Jawaban Anda:",
    key=f"jawaban_{st.session_state.phase}_{soal_index}",
    height=250
)
st.session_state.answers[f"{fase_nama} {soal_index + 1}"] = jawaban

# -------------------------------
# TOMBOL LANJUT
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
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Ujian Digital PPS | Disusun oleh Dr. Ben</p>", unsafe_allow_html=True)



