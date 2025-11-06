import streamlit as st
import pandas as pd
import datetime

# Judul aplikasi
st.title("📢 Portal Pengaduan Masyarakat")
st.subheader("Kategori: Hukum, Pendidikan, dan Kesehatan")

# Sidebar informasi
with st.sidebar:
    st.info("Silakan isi formulir di bawah untuk menyampaikan pengaduan Anda.")

# Form input pengaduan
with st.form(key='form_pengaduan'):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email Aktif")
    kategori = st.selectbox("Kategori Pengaduan", ["Hukum", "Pendidikan", "Kesehatan"])
    isi = st.text_area("Isi Pengaduan Anda", height=150)
    tanggal = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    submit = st.form_submit_button("Kirim Pengaduan")

# Simpan ke CSV jika submit
if submit:
    if nama and email and isi:
        new_data = pd.DataFrame({
            'Tanggal': [tanggal],
            'Nama': [nama],
            'Email': [email],
            'Kategori': [kategori],
            'Isi Pengaduan': [isi]
        })

        try:
            # Jika file sudah ada, tambahkan
            df_lama = pd.read_csv("pengaduan_masyarakat.csv")
            df_baru = pd.concat([df_lama, new_data], ignore_index=True)
        except FileNotFoundError:
            df_baru = new_data

        df_baru.to_csv("pengaduan_masyarakat.csv", index=False)
        st.success("✅ Pengaduan Anda telah dikirim.")
    else:
        st.warning("⚠️ Mohon lengkapi semua kolom terlebih dahulu.")

# Tampilkan daftar pengaduan
st.markdown("---")
if st.checkbox("📄 Tampilkan Semua Pengaduan"):
    try:
        data = pd.read_csv("pengaduan_masyarakat.csv")
        st.dataframe(data)
    except FileNotFoundError:
        st.info("Belum ada data pengaduan.")
