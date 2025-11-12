import io
import json
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import streamlit as st

__VERSION__ = "1.0.0"

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

def _example_products() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"product": "A", "quantity": 1000, "price": 50.0, "std_hours": 0.2},
            {"product": "B", "quantity": 400, "price": 120.0, "std_hours": 0.5},
            {"product": "C", "quantity": 200, "price": 200.0, "std_hours": 1.2},
        ]
    )


def _example_inputs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"resource": "Labor", "quantity": 120.0, "unit_cost": 6.0, "unit": "hours"},
            {"resource": "Machine", "quantity": 75.0, "unit_cost": 20.0, "unit": "machine_hours"},
            {"resource": "Materials", "quantity": 1.0, "unit_cost": 30000.0, "unit": "currency"},
            {"resource": "Energy", "quantity": 1.0, "unit_cost": 5000.0, "unit": "currency"},
            {"resource": "Overhead", "quantity": 1.0, "unit_cost": 12000.0, "unit": "currency"},
        ]
    )


def _normalize_products(df: pd.DataFrame) -> pd.DataFrame:
    required = ["product", "quantity"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Products table missing required column: {col}")
    # Ensure numeric types
    df = df.copy()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(np.nan)
    if "std_hours" in df.columns:
        df["std_hours"] = pd.to_numeric(df["std_hours"], errors="coerce").fillna(np.nan)
    return df


def _normalize_inputs(df: pd.DataFrame) -> pd.DataFrame:
    required = ["resource", "quantity", "unit_cost"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Inputs table missing required column: {col}")
    df = df.copy()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(0.0)
    if "unit" not in df.columns:
        df["unit"] = "unit"
    return df


def compute_output_value(products: pd.DataFrame, use_prices: bool = True) -> float:
    if use_prices and "price" in products.columns and products["price"].notna().any():
        return float((products["quantity"] * products["price"]).sum())
    # Fallback: price-less output proxy = sum of quantities (not ideal for mix; use std_hours if present)
    return float(products["quantity"].sum())


def compute_output_standard_hours(products: pd.DataFrame) -> Optional[float]:
    if "std_hours" in products.columns and products["std_hours"].notna().any():
        return float((products["quantity"] * products["std_hours"]).sum())
    return None


def compute_input_cost(inputs_df: pd.DataFrame) -> float:
    return float((inputs_df["quantity"] * inputs_df["unit_cost"]).sum())


def extract_partial_inputs(inputs_df: pd.DataFrame) -> Dict[str, float]:
    # Try to map common resource names to categories for partial productivity
    mapping = {
        "labor": ["labor", "tenaga kerja", "manhours", "jam kerja"],
        "machine": ["machine", "mesin", "machine hour", "mh", "jam mesin"],
        "materials": ["material", "materials", "bahan"],
        "energy": ["energy", "energi", "listrik", "bbm"],
        "overhead": ["overhead", "sewa", "depresiasi", "admin"],
    }
    totals: Dict[str, float] = {k: 0.0 for k in mapping.keys()}

    for _, r in inputs_df.iterrows():
        name = str(r["resource"]).strip().lower()
        qty = float(r["quantity"]) if pd.notna(r["quantity"]) else 0.0
        unit_cost = float(r["unit_cost"]) if pd.notna(r["unit_cost"]) else 0.0
        total_cost = qty * unit_cost
        placed = False
        for cat, keys in mapping.items():
            if any(k in name for k in keys):
                totals[cat] += total_cost
                placed = True
                break
        if not placed:
            # Sum to overhead if unknown
            totals["overhead"] += total_cost
    return totals


def deflate_value(value: float, deflator: Optional[float]) -> float:
    if deflator is None or deflator == 0:
        return value
    return value / deflator


def productivity_metrics(products: pd.DataFrame,
                         inputs_df: pd.DataFrame,
                         *,
                         use_price_output: bool = True,
                         use_standard_hour_output: bool = False,
                         price_deflator: Optional[float] = None,
                         input_deflator: Optional[float] = None) -> Dict[str, float]:
    products = _normalize_products(products)
    inputs_df = _normalize_inputs(inputs_df)

    # Output
    output_val = compute_output_value(products, use_price_output)
    std_hours_total = compute_output_standard_hours(products) if use_standard_hour_output else None

    # Inputs
    input_cost_total = compute_input_cost(inputs_df)
    partials = extract_partial_inputs(inputs_df)

    # Deflate if provided
    real_output = deflate_value(output_val, price_deflator)
    real_input_cost = deflate_value(input_cost_total, input_deflator)

    # Partial denominators (cost-based). Labor hours PP usually use hours, but we generalize using costs to keep unit-consistency.
    # Users can put labor quantity=hours and unit_cost=wage to reflect hours.

    m = {
        "gross_output_value": output_val,
        "real_output_value": real_output,
        "std_hours_output": std_hours_total if std_hours_total is not None else np.nan,
        "total_input_cost": input_cost_total,
        "real_input_cost": real_input_cost,
        "TFP_value_based": (real_output / real_input_cost) if real_input_cost else np.nan,
        # Partial productivity (value-based)
        "PP_labor": (real_output / partials.get("labor", 0.0)) if partials.get("labor", 0.0) else np.nan,
        "PP_machine": (real_output / partials.get("machine", 0.0)) if partials.get("machine", 0.0) else np.nan,
        "PP_materials": (real_output / partials.get("materials", 0.0)) if partials.get("materials", 0.0) else np.nan,
        "PP_energy": (real_output / partials.get("energy", 0.0)) if partials.get("energy", 0.0) else np.nan,
        "PP_overhead": (real_output / partials.get("overhead", 0.0)) if partials.get("overhead", 0.0) else np.nan,
    }

    if std_hours_total is not None and std_hours_total > 0:
        # Productivity per standard hour (if std_hours provided)
        m["Productivity_per_std_hour"] = real_output / std_hours_total

    return m


@st.cache_data(show_spinner=False)
def compute_metrics_df(products: pd.DataFrame, inputs_df: pd.DataFrame,
                       settings: Dict) -> pd.DataFrame:
    met = productivity_metrics(
        products,
        inputs_df,
        use_price_output=settings.get("use_price_output", True),
        use_standard_hour_output=settings.get("use_standard_hour_output", False),
        price_deflator=settings.get("price_deflator"),
        input_deflator=settings.get("input_deflator"),
    )
    df = pd.DataFrame([met]).T.reset_index()
    df.columns = ["metric", "value"]
    return df


def kaizen_compare(before_products: pd.DataFrame, before_inputs: pd.DataFrame,
                   after_products: pd.DataFrame, after_inputs: pd.DataFrame,
                   settings: Dict) -> pd.DataFrame:
    before = productivity_metrics(before_products, before_inputs,
                                  use_price_output=settings.get("use_price_output", True),
                                  use_standard_hour_output=settings.get("use_standard_hour_output", False),
                                  price_deflator=settings.get("price_deflator"),
                                  input_deflator=settings.get("input_deflator"))
    after = productivity_metrics(after_products, after_inputs,
                                 use_price_output=settings.get("use_price_output", True),
                                 use_standard_hour_output=settings.get("use_standard_hour_output", False),
                                 price_deflator=settings.get("price_deflator"),
                                 input_deflator=settings.get("input_deflator"))
    df = pd.DataFrame({"metric": list(after.keys()),
                       "before": [before.get(k, np.nan) for k in after.keys()],
                       "after": [after.get(k, np.nan) for k in after.keys()]})
    df["change_abs"] = df["after"] - df["before"]
    df["change_pct"] = np.where(df["before"].abs() > 0, (df["after"] / df["before"] - 1.0) * 100.0, np.nan)
    return df


def national_aggregate(dataset: pd.DataFrame, settings: Dict) -> pd.DataFrame:
    """
    Expect long-form dataset with columns:
    company, period, table, product/resource, quantity, price, std_hours, unit_cost
    Where table in {"product","input"}. Flexible; missing cols tolerated.
    Aggregation = sum of outputs and inputs across companies, then compute metrics.
    """
    df = dataset.copy()
    for c in ["quantity", "price", "std_hours", "unit_cost"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    # Build nationwide products & inputs for each (period)
    results = []
    for period, group in df.groupby(df.get("period", "ALL")):
        prods = group[group["table"] == "product"][['product','quantity','price','std_hours']].copy() if 'table' in group.columns else group[group['type']=='product'][['product','quantity','price','std_hours']]
        inputs = group[group["table"] == "input"][['resource','quantity','unit_cost','unit']].copy() if 'table' in group.columns else group[group['type']=='input'][['resource','quantity','unit_cost','unit']]
        if prods.empty:
            prods = _example_products()
        if inputs.empty:
            inputs = _example_inputs()
        m = productivity_metrics(prods, inputs,
                                 use_price_output=settings.get("use_price_output", True),
                                 use_standard_hour_output=settings.get("use_standard_hour_output", False),
                                 price_deflator=settings.get("price_deflator"),
                                 input_deflator=settings.get("input_deflator"))
        m["period"] = period
        results.append(m)
    return pd.DataFrame(results)


# --------------------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------------------

st.set_page_config(page_title="National-Scale Productivity & Kaizen Analyzer", layout="wide")

st.title("📈 National-Scale Productivity & Kaizen Analyzer")
st.caption(
    "Flexible Streamlit app for mixed-product productivity measurement and Kaizen (continuous improvement) analysis. "
    f"Version {__VERSION__} – {datetime.now():%Y-%m-%d}"
)

with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("Choose how outputs & inputs are aggregated.")
    use_price_output = st.toggle("Aggregate output by VALUE (quantity × price)", value=True,
                                 help="Recommended for mixed product portfolios. If disabled, output proxy falls back to quantity sum.")
    use_standard_hour_output = st.toggle("Also compute output in STANDARD HOURS (Σ qty × std_hours)", value=True,
                                         help="Requires std_hours per product; useful for manufacturing mix.")
    st.markdown("---")
    st.subheader("Deflators (optional)")
    price_deflator = st.number_input("Output price deflator (e.g., CPI index for base year)", min_value=0.0, value=1.0, step=0.01,
                                     help="Real output = nominal output / deflator.")
    input_deflator = st.number_input("Input cost deflator (e.g., input price index)", min_value=0.0, value=1.0, step=0.01,
                                     help="Real input = nominal input / deflator.")
    st.markdown("---")
    st.subheader("Download")
    auto_filename = f"productivity_report_{datetime.now():%Y%m%d_%H%M%S}.csv"

mode = st.tabs(["Single Period", "Kaizen Compare", "National Aggregation", "Help & Data Specs"])

# --------------------------------------------------------------------------------------
# Tab 1: Single Period
# --------------------------------------------------------------------------------------
with mode[0]:
    st.subheader("Single Period Productivity")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Products** (one row per SKU/product)")
        st.caption("Required columns: product, quantity. Optional: price, std_hours.")
        prod_file = st.file_uploader("Upload products CSV (optional)", type=["csv"], key="prod_single")
        if prod_file:
            products_df = pd.read_csv(prod_file)
        else:
            products_df = _example_products()
        products_df = st.data_editor(products_df, num_rows="dynamic", use_container_width=True, key="prod_edit_single")

    with col2:
        st.markdown("**Inputs/Resources** (labor, machine, materials, etc.)")
        st.caption("Required columns: resource, quantity, unit_cost. Optional: unit")
        inp_file = st.file_uploader("Upload inputs CSV (optional)", type=["csv"], key="inp_single")
        if inp_file:
            inputs_df = pd.read_csv(inp_file)
        else:
            inputs_df = _example_inputs()
        inputs_df = st.data_editor(inputs_df, num_rows="dynamic", use_container_width=True, key="inp_edit_single")

    settings = {
        "use_price_output": use_price_output,
        "use_standard_hour_output": use_standard_hour_output,
        "price_deflator": None if price_deflator in (0, 1) else price_deflator,
        "input_deflator": None if input_deflator in (0, 1) else input_deflator,
    }

    try:
        metrics_df = compute_metrics_df(products_df, inputs_df, settings)
        st.success("Metrics computed.")
        st.dataframe(metrics_df, use_container_width=True)

        csv = metrics_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download metrics CSV", data=csv, file_name=auto_filename, mime="text/csv")
    except Exception as e:
        st.error(f"Error computing metrics: {e}")

# --------------------------------------------------------------------------------------
# Tab 2: Kaizen Compare
# --------------------------------------------------------------------------------------
with mode[1]:
    st.subheader("Kaizen: Before vs After")
    st.caption("Compare productivity between two periods, teams, lines, or improvement states.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Before** – Products & Inputs")
        bpf = st.file_uploader("Before products CSV", type=["csv"], key="bp")
        bif = st.file_uploader("Before inputs CSV", type=["csv"], key="bi")
        before_products = pd.read_csv(bpf) if bpf else _example_products()
        before_inputs = pd.read_csv(bif) if bif else _example_inputs()
        before_products = st.data_editor(before_products, num_rows="dynamic", use_container_width=True, key="bp_edit")
        before_inputs = st.data_editor(before_inputs, num_rows="dynamic", use_container_width=True, key="bi_edit")

    with col2:
        st.markdown("**After** – Products & Inputs")
        apf = st.file_uploader("After products CSV", type=["csv"], key="ap")
        aif = st.file_uploader("After inputs CSV", type=["csv"], key="ai")
        after_products = pd.read_csv(apf) if apf else _example_products()
        after_inputs = pd.read_csv(aif) if aif else _example_inputs()
        after_products = st.data_editor(after_products, num_rows="dynamic", use_container_width=True, key="ap_edit")
        after_inputs = st.data_editor(after_inputs, num_rows="dynamic", use_container_width=True, key="ai_edit")

    settings2 = settings

    if st.button("Compute Kaizen Comparison", type="primary"):
        try:
            kdf = kaizen_compare(before_products, before_inputs, after_products, after_inputs, settings2)
            st.success("Kaizen comparison computed.")
            st.dataframe(kdf, use_container_width=True)

            # Highlights
            tfp_row = kdf[kdf["metric"] == "TFP_value_based"].iloc[0] if not kdf[kdf["metric"] == "TFP_value_based"].empty else None
            if tfp_row is not None:
                st.metric("TFP change (%)", value=f"{tfp_row['change_pct']:.2f}%")

            csv2 = kdf.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Kaizen CSV", data=csv2,
                               file_name=f"kaizen_compare_{datetime.now():%Y%m%d_%H%M%S}.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------------------------------------------------------------------------
# Tab 3: National Aggregation
# --------------------------------------------------------------------------------------
with mode[2]:
    st.subheader("National Aggregation (Multi-company, Multi-period)")
    st.caption("Upload a long-form dataset with columns: company, period, table (product/input), product/resource, quantity, price, std_hours, unit_cost, unit")
    nat = st.file_uploader("Upload national dataset CSV", type=["csv"], key="nat")

    if nat:
        nat_df = pd.read_csv(nat)
    else:
        # Build a small demo dataset
        demo_prods = _example_products(); demo_prods["company"] = "DemoCo"; demo_prods["period"] = "2025Q3"; demo_prods["table"] = "product"
        demo_inputs = _example_inputs(); demo_inputs["company"] = "DemoCo"; demo_inputs["period"] = "2025Q3"; demo_inputs["table"] = "input"
        nat_df = pd.concat([
            demo_prods.rename(columns={"product":"product"})[["company","period","table","product","quantity","price","std_hours"]],
            demo_inputs[["company","period","table","resource","quantity","unit_cost","unit"]],
        ], ignore_index=True)

    st.dataframe(nat_df, use_container_width=True)

    if st.button("Compute National Metrics", type="primary"):
        try:
            agg = national_aggregate(nat_df, settings)
            st.dataframe(agg, use_container_width=True)
            csv3 = agg.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download National Metrics CSV", data=csv3,
                               file_name=f"national_metrics_{datetime.now():%Y%m%d_%H%M%S}.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------------------------------------------------------------------------
# Tab 4: Help
# --------------------------------------------------------------------------------------
with mode[3]:
    st.subheader("Data Specs & Notes")
    st.markdown(
        """
        ### Products table (per period)
        - **Required**: `product`, `quantity`
        - **Optional**: `price` (currency per unit), `std_hours` (standard labor/machine hours per unit)

        ### Inputs/Resources table (per period)
        - **Required**: `resource`, `quantity`, `unit_cost`
        - **Optional**: `unit` (e.g., hours, currency)

        ### Methods
        - **Value-based output** (`Σ qty × price`) recommended for product mix.
        - **Standard hours** allow additional productivity metric independent of prices.
        - **TFP** (value-based) = Real Output Value / Real Input Cost (use deflators to adjust for price changes).
        - **Partial productivity** computed against categorized input costs (labor, machine, materials, energy, overhead).

        ### Kaizen
        - Compare `Before` vs `After` states. App shows absolute and percentage change for each metric.

        ### National Aggregation
        - Upload long-form data combining many companies & periods. The app aggregates outputs & inputs and computes metrics per period.

        ### Tips
        - Use consistent currency and units.
        - If your labor PP must be per **hour**, set `quantity = hours` and `unit_cost = average wage`. Interpret carefully.
        - Provide **deflators** (e.g., CPI, PPI) to get *real* productivity over time.
        - You can extend the resource categories by renaming rows (mapping handled heuristically; unknowns go to overhead).
        """
    )

    st.info("This app is template-style and intentionally generic so it can fit manufacturing, services, healthcare, logistics, etc.")

st.toast("Ready. Load your data or edit the examples.", icon="✅")
