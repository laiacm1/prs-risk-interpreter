import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="PRS Risk Interpreter", layout="wide")

st.title("PRS Risk Interpreter")

st.markdown("""
Interactive platform visualizing ancestry-dependent polygenic risk score (PRS) interpretation and threshold distortion.
""")

# Simulated placeholder data
np.random.seed(42)

eur = np.random.normal(0, 1, 1000)
sas = np.random.normal(0.3, 1, 1000)

threshold_percentile = st.slider(
    "Select EUR percentile threshold",
    50,
    99,
    90
)

threshold = np.percentile(eur, threshold_percentile)

sas_above = (sas > threshold).mean() * 100

fig = go.Figure()

fig.add_histogram(
    x=eur,
    name="EUR",
    opacity=0.6
)

fig.add_histogram(
    x=sas,
    name="SAS",
    opacity=0.6
)

fig.add_vline(
    x=threshold,
    line_dash="dash",
    annotation_text=f"EUR {threshold_percentile}th percentile"
)

fig.update_layout(
    barmode='overlay',
    title="PRS Distribution Comparison",
    xaxis_title="PRS",
    yaxis_title="Count"
)

st.plotly_chart(fig, use_container_width=True)

st.metric(
    "Percent of SAS individuals above EUR threshold",
    f"{sas_above:.1f}%"
)

st.markdown("""
### Why this matters

Polygenic risk scores trained primarily on European populations may not transfer cleanly across ancestries. This can lead to threshold distortion and differences in clinical interpretation.
""")
