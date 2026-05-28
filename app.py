import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="PRS Risk Interpreter", layout="wide")

st.title("PRS Risk Interpreter")
st.markdown(
    "Interactive platform visualizing ancestry-dependent polygenic risk score (PRS) interpretation, threshold distortion, and recalibration."
)

threshold_df = pd.read_csv("data/real_individual_threshold_inflation.csv")
calibration_df = pd.read_csv("data/real_1000G_raw_vs_calibrated_thresholds.csv")

st.sidebar.header("Controls")

percentiles = sorted(threshold_df["EUR_percentile_cutoff"].unique())

selected_percentile = st.sidebar.select_slider(
    "EUR percentile cutoff",
    options=percentiles,
    value=90 if 90 in percentiles else percentiles[len(percentiles)//2]
)

row = threshold_df[threshold_df["EUR_percentile_cutoff"] == selected_percentile].iloc[0]

cutoff = row["cutoff"]
eur_rate = row["EUR_high_risk_rate"]
sas_rate = row["SAS_high_risk_rate"]
ratio = row["SAS_EUR_ratio"]

st.subheader("Threshold Distortion Explorer")

col1, col2, col3 = st.columns(3)

col1.metric("EUR high-risk rate", f"{eur_rate:.1%}")
col2.metric("SAS high-risk rate", f"{sas_rate:.1%}")
col3.metric("SAS/EUR distortion ratio", f"{ratio:.2f}x")

st.markdown(
    f"""
    At the **EUR {selected_percentile}th percentile cutoff**, the score threshold is **{cutoff:.4f}**.  
    By definition, about **{eur_rate:.1%}** of EUR individuals exceed this threshold.  
    In SAS individuals, **{sas_rate:.1%}** exceed the same EUR-defined threshold.
    """
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=threshold_df["EUR_percentile_cutoff"],
        y=threshold_df["SAS_EUR_ratio"],
        mode="lines+markers",
        name="SAS/EUR distortion ratio"
    )
)

fig.add_vline(
    x=selected_percentile,
    line_dash="dash",
    annotation_text=f"Selected: {selected_percentile}th"
)

fig.update_layout(
    title="Threshold Distortion Across EUR Percentile Cutoffs",
    xaxis_title="EUR Percentile Cutoff",
    yaxis_title="SAS/EUR High-Risk Classification Ratio",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Raw vs Recalibrated Threshold Error")

available_pops = sorted(calibration_df["population"].unique())

selected_pop = st.selectbox(
    "Compare recalibration for population",
    available_pops,
    index=available_pops.index("SAS") if "SAS" in available_pops else 0
)

pop_df = calibration_df[calibration_df["population"] == selected_pop]

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=pop_df["percentile"],
        y=pop_df["raw_error"],
        mode="lines+markers",
        name="Raw error"
    )
)

fig2.add_trace(
    go.Scatter(
        x=pop_df["percentile"],
        y=pop_df["z_error"],
        mode="lines+markers",
        name="After z-score recalibration"
    )
)

fig2.add_hline(y=0, line_dash="dash")

fig2.update_layout(
    title=f"Threshold Error Before vs After Recalibration ({selected_pop})",
    xaxis_title="EUR Percentile Cutoff",
    yaxis_title="Classification Error",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Why this matters")

st.markdown(
    """
    Polygenic risk scores are probabilistic tools. A score threshold calibrated in one ancestry group may not transfer cleanly to another because allele frequencies, linkage disequilibrium, and score architecture differ across populations.

    This tool visualizes how an EUR-defined PRS threshold can classify individuals from another population at different rates, and how ancestry-specific recalibration can reduce threshold distortion.

    **Educational/research use only. This is not a clinical risk calculator.  **
    """
)
