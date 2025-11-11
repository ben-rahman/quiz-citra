import streamlit as st
import pandas as pd
import numpy as np
import locale

# ----------------------------------
# KONFIGURASI LOKAL
# ----------------------------------
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

# ----------------------------------
# KONFIG DASHBOARD
# ----------------------------------
st.set_page_config(page_title="Kalkulator Produktivitas", layout="wide")

st.title("📊 Kalkulator Produktivitas Tenaga Kerja")
st.caption("Versi dengan format angka Indonesia (1.000.000,00) — dirancang oleh Dr. Benrahman 🇮🇩")

# ----------------------------------
# FUNGSI FORMAT & PARSING
# ----------------------------------
def parse_currency(value_str):
    """Mengubah input teks seperti '1.000.000,25' jadi float"""
    if not value_str:
        return 0.0
    try:
        value_str = value_str.replace(".", "").replace(",", ".")
        return float(value_str)
    except ValueError:
        return 0.0

def format_currency(value):
    """Format float ke tampilan rupiah: 1.000.000,00"""
    try:
        return locale.format_string("%.2f", value, grouping=True)
    except:
        return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

# ----------------------------------
# UTILITAS PRODUKTIVITAS
# ----------------------------------
def hitung_indikator(output, workers, hours, labour_cost):
    lp = output / workers if workers > 0 else np.nan
    hp = output / hours if hours > 0 else np.nan
    wp = output / labour_cost if labour_cost > 0 else np.nan
    return lp, hp, wp

def hitung_skor_indikator(value, target):
    if target is None or target == 0 or np.isnan(value):
        return np.nan
    return min(100.0, (value / target) * 100.0)

def hitung_indeks(lp, hp, wp, weights, targets):
    w_lp, w_hp, w_wp = weights
    t_lp, t_hp, t_wp = targets
    s_lp = hitung_skor_indikator(lp, t_lp)
    s_hp = hitung_skor_indikator(hp, t_hp)
    s_wp = hitung_skor_indikator(wp, t_wp)
    skor, bobot = [], []
    if not np.isnan(s_lp) and w_lp > 0: skor.append(s_lp); bobot.append(w_lp)
    if not np.isnan(s_hp) and w_hp > 0: skor.append(s_hp); bobot.append(w_hp)
    if not np.isnan(s_wp) and w_wp > 0: skor.append(s_wp); bobot.append(w_wp)
    if not skor: return np.nan
    bobot = np.array(bobot) / np.sum(bobot)
    return float(np.sum(bobot * np.array(skor)))

# ----------------------------------
# PENGATURAN SIDEBAR
# ----------------------------------
st.sidebar.header("⚙️ Pengaturan")

mode = st.sidebar.radio("Pilih mode:", ("Input Manual", "Upload CSV (Multi Unit)"))
w_lp = st.sidebar.slider("Bobot Produktivitas Tenaga Kerja", 0, 100, 40, 5)
w_hp = st.sidebar.slider("Bobot per Jam Kerja", 0, 100, 30, 5)
w_wp = st.sidebar.slider("Bobot per Upah", 0, 100, 30, 5)
total_bobot = w_lp + w_hp + w_wp
weights = (w_lp/total_bobot, w_hp/total_bobot, w_wp/total_bobot) if total_bobot != 0 else (0, 0, 0)
st.sidebar.caption(f"Total bobot: {total_bobot} (dinormalisasi otomatis)")

target_lp = st.sidebar.text_input("🎯 Target Output/Pekerja (Rp)", "0,00")
target_hp = st.sidebar.text_input("🎯 Target Output/Jam (Rp)", "0,00")
target_wp = st.sidebar.text_input("🎯 Target Output/Biaya TK", "0,0000")

# ----------------------------------
# MODE 1: INPUT MANUAL
# ----------------------------------
if mode == "Input Manual":
    st.header("🧮 Input Manual – Satu Perusahaan")

    nama = st.text_input("Nama Perusahaan / Unit", "PT Contoh Produktif")
    periode = st.text_input("Periode (mis. 2024-Q1)", "2024")

    col1, col2 = st.columns(2)
    with col1:
        output_str = st.text_input("Total Output (Rp)", "1.000.000,00")
        workers_str = st.text_input("Jumlah Tenaga Kerja", "10,00")
        labour_str = st.text_input("Total Biaya Tenaga Kerja (Rp)", "300.000,00")

    with col2:
        hours_str = st.text_input("Total Jam Kerja", "1.200,00")

    # Parsing ke float
    output = parse_currency(output_str)
    workers = parse_currency(workers_str)
    labour_cost = parse_currency(labour_str)
    hours = parse_currency(hours_str)

    if st.button("Hitung Produktivitas"):
        lp, hp, wp = hitung_indikator(output, workers, hours, labour_cost)
        indeks = hitung_indeks(lp, hp, wp, weights, (
            parse_currency(target_lp), parse_currency(target_hp), parse_currency(target_wp)
        ))

        st.subheader("📈 Hasil Perhitungan")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Output/Pekerja", format_currency(lp))
        col_b.metric("Output/Jam Kerja", format_currency(hp))
        col_c.metric("Output/Biaya TK", format_currency(wp))
        col_d.metric("Indeks Produktivitas", f"{indeks:,.2f}" if not np.isnan(indeks) else "N/A")

        st.markdown("---")
        st.markdown(f"""
        **{nama} – Periode {periode}**
        - Output total: Rp {format_currency(output)}
        - Tenaga kerja: {format_currency(workers)}
        - Total jam kerja: {format_currency(hours)}
        - Biaya tenaga kerja: Rp {format_currency(labour_cost)}
        """)

# ----------------------------------
# MODE 2: UPLOAD CSV
# ----------------------------------
else:
    st.header("📂 Upload CSV – Multi Unit")
    st.markdown("Struktur: `unit,output,workers,hours,labour_cost`")

    file = st.file_uploader("Upload file CSV", type=["csv"])
    if file:
        df = pd.read_csv(file)
        lp_list, hp_list, wp_list, idx_list = [], [], [], []
        for _, r in df.iterrows():
            lp, hp, wp = hitung_indikator(r["output"], r["workers"], r["hours"], r["labour_cost"])
            idx = hitung_indeks(lp, hp, wp, weights, (
                parse_currency(target_lp), parse_currency(target_hp), parse_currency(target_wp)
            ))
            lp_list.append(lp); hp_list.append(hp); wp_list.append(wp); idx_list.append(idx)

        df["prod_per_worker"], df["prod_per_hour"], df["prod_per_wage"], df["productivity_index"] = lp_list, hp_list, wp_list, idx_list
        df_fmt = df.copy()
        for c in ["output","workers","hours","labour_cost","prod_per_worker","prod_per_hour","prod_per_wage","productivity_index"]:
            df_fmt[c] = df_fmt[c].apply(lambda x: format_currency(x) if pd.notna(x) else "")
        st.dataframe(df_fmt)

# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("---")
st.caption("Kalkulator Produktivitas 🇮🇩 – versi format Indonesia (1.000.000,00) | oleh Dr. Benrahman 😎")
