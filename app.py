import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Cross-Ancestry PRS Explorer",
    page_icon="🧬",
    layout="wide"
)

DATA_DIR = Path("data")

DATA_DIR = Path("data")

@st.cache_data
def load_csv(name):
    return pd.read_csv(DATA_DIR / name)

summary = load_csv("website_corrected_prs_summary_by_ancestry.csv")
recal = load_csv("website_recalibration_summary.csv")
zcheck = load_csv("website_zscore_validation_by_ancestry.csv")
ld_retention = load_csv("FINAL_pruning_signal_retention_by_chr.csv")
gene_summary = load_csv("FINAL_top_driver_gene_signal_summary.csv")

st.title("Cross-Ancestry PRS Explorer")
st.markdown(
    """
    ### Biological Interpretation

    Mapping the strongest distortion-driving variants to nearby genes revealed several established
    Type 2 Diabetes loci among the top contributors, including **ADAMTS9, KCNQ1, ST6GAL1, PPARG,
    JAZF1, and CDKN2B-AS1**.

    Rather than being driven by a single gene or genomic region, the cross-ancestry signal remains
    distributed across many loci. Even the strongest individual genes explain only a small fraction
    of the total distortion, supporting a highly polygenic architecture.

    Pathway enrichment analysis of the top driver genes identified significant enrichment for the
    **Type II Diabetes Mellitus** pathway, with additional enrichment observed for **insulin
    secretion** and related metabolic processes.

    Together, these results suggest that cross-ancestry PRS distortion is not simply a statistical
    artifact. The largest ancestry-dependent shifts occur at loci already implicated in diabetes
    biology, indicating that differences in population allele frequencies at disease-relevant genes
    contribute to portability failure.
    """
)
st.info(
    "Research use only. This is not a clinical risk calculator."
)

# -------------------------
# Top validation metrics
# -------------------------

st.subheader("Final Validation Snapshot")

col1, col2, col3, col4 = st.columns(4)

col1.metric("1000G individuals", "2,504")
col2.metric("SAS above EUR 90th", "81.4%")
col3.metric("After recalibration", "11.0%")
col4.metric("LD signal retained", "99.34%")

st.markdown(
    """
    The corrected real-genotype PRS preserves strong ancestry structure. Applying a European-defined
    high-risk threshold to South Asian individuals produces severe threshold distortion, while
    ancestry-specific z-score recalibration largely corrects the issue.
    """
)

st.divider()

# -------------------------
# PRS ancestry summary
# -------------------------

st.subheader("Corrected PRS Distribution Summary by Ancestry")

summary_display = summary.copy()
summary_display = summary_display.reset_index() if "super_pop" not in summary_display.columns else summary_display
st.dataframe(summary_display, use_container_width=True)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=summary_display["super_pop"],
        y=summary_display["mean"],
        error_y=dict(type="data", array=summary_display["std"]),
        name="Mean PRS"
    )
)

fig.update_layout(
    title="Mean Corrected Genome-wide PRS by Ancestry",
    xaxis_title="Ancestry group",
    yaxis_title="Mean corrected PRS",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# Threshold recalibration
# -------------------------

st.subheader("Threshold Distortion and Recalibration")

selected_percentile = st.select_slider(
    "Select European percentile cutoff",
    options=list(recal["percentile_cutoff"]),
    value=90
)

row = recal[recal["percentile_cutoff"] == selected_percentile].iloc[0]

c1, c2, c3 = st.columns(3)

c1.metric("Expected above rate", f"{1 - selected_percentile/100:.1%}")
c2.metric("SAS raw above rate", f"{row['SAS_raw_above_rate']:.1%}")
c3.metric("SAS recalibrated above rate", f"{row['SAS_recalibrated_above_rate']:.1%}")

st.markdown(
    f"""
    At the **European {selected_percentile}th percentile cutoff**, the raw PRS classifies
    **{row['SAS_raw_above_rate']:.1%}** of South Asian individuals above the threshold.
    After ancestry-specific recalibration, this falls to **{row['SAS_recalibrated_above_rate']:.1%}**.
    """
)

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=recal["percentile_cutoff"],
        y=recal["SAS_raw_above_rate"],
        mode="lines+markers",
        name="SAS raw above rate"
    )
)

fig2.add_trace(
    go.Scatter(
        x=recal["percentile_cutoff"],
        y=recal["SAS_recalibrated_above_rate"],
        mode="lines+markers",
        name="SAS recalibrated above rate"
    )
)

fig2.add_trace(
    go.Scatter(
        x=recal["percentile_cutoff"],
        y=1 - recal["percentile_cutoff"] / 100,
        mode="lines+markers",
        name="Expected above rate"
    )
)

fig2.update_layout(
    title="Raw vs Recalibrated Threshold Transfer",
    xaxis_title="European percentile cutoff",
    yaxis_title="Fraction above threshold",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=recal["percentile_cutoff"],
        y=recal["error_reduction_percent"],
        mode="lines+markers",
        name="Error reduction"
    )
)

fig3.update_layout(
    title="Error Reduction After Ancestry-Specific Recalibration",
    xaxis_title="European percentile cutoff",
    yaxis_title="Error reduction (%)",
    height=450
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -------------------------
# Z-score validation
# -------------------------

st.subheader("Z-Score Recalibration Validation")

z_display = zcheck.reset_index() if "super_pop" not in zcheck.columns else zcheck
st.dataframe(z_display, use_container_width=True)

st.markdown(
    """
    After within-ancestry z-score standardization, each ancestry group has mean approximately 0
    and standard deviation approximately 1. This confirms that recalibration behaved as expected.
    """
)

st.divider()

# -------------------------
# LD pruning validation
# -------------------------

st.subheader("LD Pruning Validation")

total_dense = ld_retention["dense_abs_delta"].sum()
total_pruned = ld_retention["pruned_abs_delta"].sum()
overall_retained = total_pruned / total_dense * 100
removed_snps = ld_retention["removed_snps"].sum()
dense_snps = ld_retention["dense_snps"].sum()

c1, c2, c3 = st.columns(3)

c1.metric("Top driver SNPs tested", f"{dense_snps}")
c2.metric("SNPs removed by pruning", f"{removed_snps}")
c3.metric("Signal retained", f"{overall_retained:.2f}%")

fig4 = go.Figure()

fig4.add_trace(
    go.Bar(
        x=ld_retention["chromosome"],
        y=ld_retention["fraction_signal_retained"] * 100,
        name="Signal retained"
    )
)

fig4.update_layout(
    title="PRS Shift Signal Retained After LD Pruning",
    xaxis_title="Chromosome",
    yaxis_title="Signal retained (%)",
    height=450
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    """
    LD pruning removed only a tiny fraction of top driver SNPs and retained nearly all of the
    cross-ancestry signal. This supports the interpretation that PRS distortion is not mainly caused
    by a few highly correlated LD blocks.
    """
)

st.divider()

# -------------------------
# Gene biology
# -------------------------

st.subheader("Top Gene-Level Contributors")

top_n = st.slider("Number of genes to show", 5, 30, 15)

top_genes = gene_summary.head(top_n)

fig5 = go.Figure()

fig5.add_trace(
    go.Bar(
        x=top_genes["total_abs_delta"],
        y=top_genes["gene"],
        orientation="h",
        name="Total absolute contribution"
    )
)

fig5.update_layout(
    title="Top Gene-Level Contributors to Cross-Ancestry PRS Distortion",
    xaxis_title="Total absolute contribution",
    yaxis_title="Gene",
    height=600,
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig5, use_container_width=True)

st.dataframe(top_genes, use_container_width=True)

st.markdown(
    """
    Several high-signal genes are connected to diabetes or cardiometabolic biology, including
    ADAMTS9, KCNQ1, ST6GAL1, PPARG, CDKN2B-AS1, and JAZF1. The next biological layer is to
    investigate whether top driver variants act as eQTLs in relevant tissues such as pancreas,
    liver, adipose, muscle, or blood.
    """
)

st.divider()

# -------------------------
# Final conclusion
# -------------------------

st.subheader("Current Project Claim")

st.markdown(
    """
    **European-derived Type 2 Diabetes PRSs encode strong ancestry structure that produces severe
    cross-population threshold distortion. Much of this portability failure behaves like a calibration
    and architecture problem rather than complete ranking collapse. The signal persists after LD
    pruning and appears to arise from many weakly correlated variants with ancestry-dependent
    allele-frequency and effect-size architecture.**
    """
)
