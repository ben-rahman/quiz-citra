import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------------
# CONFIG DASHBOARD
# ----------------------------------
st.set_page_config(
    page_title="Kalkulator Produktivitas",
    layout="wide",
)

st.title("📊 Kalkulator Produktivitas Tenaga Kerja")
st.caption("Minimum Viable Product (MVP) – dirancang untuk perusahaan, manajer, dan pemangku kepentingan kebijakan")
st.caption("Draft awal dicetuskan oleh Dr. Benrahman, semoga ada masukan dan saran untuk penyempurnaan menuju sistem nasional 🇮🇩")

# ----------------------------------
# SIDEBAR – MODE & PENGATURAN
# ----------------------------------
st.sidebar.header("⚙️ Pengaturan")

mode = st.sidebar.radio(
    "Pilih mode:",
    ("Input Manual (Single Perusahaan/Unit)", "Upload CSV (Multi Unit)"),
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Bobot Indeks Produktivitas")

w_lp = st.sidebar.slider("Bobot Produktivitas Tenaga Kerja", 0, 100, 40, 5)
w_hp = st.sidebar.slider("Bobot Produktivitas per Jam Kerja", 0, 100, 30, 5)
w_wp = st.sidebar.slider("Bobot Produktivitas per Upah", 0, 100, 30, 5)

weight_sum = w_lp + w_hp + w_wp
if weight_sum == 0:
    weights = (0, 0, 0)
else:
    weights = (w_lp / weight_sum, w_hp / weight_sum, w_wp / weight_sum)

st.sidebar.markdown(
    f"**Total bobot:** {weight_sum} (dinormalisasi otomatis menjadi 1.0 di perhitungan indeks)"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Target (Opsional, per Periode)")
st.sidebar.caption("Jika target = 0, indikator tersebut tidak dipakai untuk skor indeks.")

target_lp = st.sidebar.number_input(
    "Target Produktivitas Tenaga Kerja (Output / Pekerja)",
    min_value=0.0,
    value=0.0,
    step=100000.0,
    format="%.2f",
)
target_hp = st.sidebar.number_input(
    "Target Produktivitas per Jam (Output / Jam Kerja)",
    min_value=0.0,
    value=0.0,
    step=1000.0,
    format="%.2f",
)
target_wp = st.sidebar.number_input(
    "Target Produktivitas per Upah (Output / Biaya Tenaga Kerja)",
    min_value=0.0,
    value=0.0,
    step=0.1,
    format="%.4f",
)

# ----------------------------------
# FUNGSI UTILITAS
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

    skor_list, bobot_list = [], []
    if not np.isnan(s_lp) and w_lp > 0: skor_list.append(s_lp); bobot_list.append(w_lp)
    if not np.isnan(s_hp) and w_hp > 0: skor_list.append(s_hp); bobot_list.append(w_hp)
    if not np.isnan(s_wp) and w_wp > 0: skor_list.append(s_wp); bobot_list.append(w_wp)
    if len(skor_list) == 0: return np.nan

    bobot_arr = np.array(bobot_list) / np.sum(bobot_list)
    return float(np.sum(bobot_arr * np.array(skor_list)))

# ----------------------------------
# MODE 1: INPUT MANUAL
# ----------------------------------
if mode == "Input Manual (Single Perusahaan/Unit)":
    st.header("🧮 Perhitungan Produktivitas – Input Manual")
    col1, col2 = st.columns(2)

    with col1:
        nama_unit = st.text_input("Nama Perusahaan / Unit", "PT Contoh Produktif")
        periode = st.text_input("Periode (mis. 2024-Q1 / 2024)", "2024")
        output = st.number_input("Total Output (Rp)", min_value=0.0, value=1_000_000_000.0, step=100_000_000.0, format="%.2f")
        workers = st.number_input("Jumlah Tenaga Kerja", min_value=1, value=100, step=1)

    with col2:
        st.markdown("### Opsi Jam Kerja")
        use_auto_hours = st.checkbox("Hitung otomatis jam kerja", value=True)
        if use_auto_hours:
            hours_per_week = st.number_input("Jam kerja/minggu per pekerja", 1.0, 40.0, 1.0)
            weeks_per_period = st.number_input("Jumlah minggu (mis. 13 untuk triwulan)", 1.0, 13.0, 1.0)
            total_hours = hours_per_week * weeks_per_period * workers
        else:
            total_hours = st.number_input("Total Jam Kerja", min_value=1.0, value=40_000.0, step=1000.0)
        labour_cost = st.number_input("Total Biaya Tenaga Kerja (Rp)", min_value=0.0, value=300_000_000.0, step=50_000_000.0, format="%.2f")

    if st.button("Hitung Produktivitas"):
        lp, hp, wp = hitung_indikator(output, workers, total_hours, labour_cost)
        indeks = hitung_indeks(lp, hp, wp, weights, (target_lp, target_hp, target_wp))

        st.subheader("📈 Hasil Perhitungan")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Produktivitas Tenaga Kerja", f"{lp:,.2f}", "Output / pekerja")
        col_b.metric("Produktivitas per Jam Kerja", f"{hp:,.2f}", "Output / jam")
        col_c.metric("Produktivitas per Upah", f"{wp:,.4f}", "Output / Rp biaya TK")
        col_d.metric("Indeks Produktivitas (0–100)", f"{indeks:,.2f}" if not np.isnan(indeks) else "N/A")

        st.markdown("---")
        st.markdown("### 📋 Ringkasan")
        st.write(
            f"**{nama_unit}** – Periode **{periode}**\n\n"
            f"- Output total: Rp {output:,.0f}\n"
            f"- Jumlah tenaga kerja: {workers:,}\n"
            f"- Total jam kerja: {total_hours:,.0f}\n"
            f"- Total biaya tenaga kerja: Rp {labour_cost:,.0f}"
        )

        df_plot = pd.DataFrame({"Indikator": ["Output/Worker","Output/Hour","Output/Labour Cost"], "Nilai": [lp, hp, wp]})
        st.bar_chart(df_plot.set_index("Indikator"))

# ----------------------------------
# MODE 2: UPLOAD CSV
# ----------------------------------
else:
    st.header("📂 Perhitungan Produktivitas – Multi Unit (CSV)")
    st.markdown("**Struktur CSV yang diharapkan:** `unit, output, workers, hours, labour_cost`")

    uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_cols = ["unit", "output", "workers", "labour_cost"]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                st.error(f"Kolom berikut wajib ada di CSV: {missing}")
            else:
                if "hours" not in df.columns: df["hours"] = np.nan

                lp_list, hp_list, wp_list, idx_list = [], [], [], []
                for _, row in df.iterrows():
                    lp, hp, wp = hitung_indikator(row["output"], row["workers"], row["hours"], row["labour_cost"])
                    idx = hitung_indeks(lp, hp, wp, weights, (target_lp, target_hp, target_wp))
                    lp_list.append(lp); hp_list.append(hp); wp_list.append(wp); idx_list.append(idx)

                df["prod_per_worker"], df["prod_per_hour"], df["prod_per_wage"], df["productivity_index"] = lp_list, hp_list, wp_list, idx_list

                # Formatting angka
                df_fmt = df.copy()
                for col in ["output","workers","hours","labour_cost","prod_per_worker","prod_per_hour","prod_per_wage","productivity_index"]:
                    if col in df_fmt.columns:
                        df_fmt[col] = df_fmt[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "")

                st.subheader("📋 Hasil Perhitungan per Unit")
                st.dataframe(df_fmt)

                st.markdown("### 📊 Grafik Produktivitas per Unit")
                st.bar_chart(df.set_index("unit")["prod_per_worker"])
                if df["productivity_index"].notna().any():
                    st.markdown("### ⭐ Indeks Produktivitas per Unit")
                    st.bar_chart(df.set_index("unit")["productivity_index"])

                # Optional: download CSV hasil
                csv_out = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Hasil CSV", data=csv_out, file_name="hasil_kalkulator_produktivitas.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Terjadi error saat membaca CSV: {e}")

# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("---")
st.caption("MVP Kalkulator Produktivitas – fondasi sistem monitoring nasional untuk efisiensi dan daya saing perusahaan Indonesia.")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 MVP Kalkulator Produktivitas | Dibuat oleh Dr. Benrahman 😎</p>", unsafe_allow_html=True)
