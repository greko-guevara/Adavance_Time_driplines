import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------
st.set_page_config(
    page_title="Hydraulic Advance Time – Dripline Model",
    layout="wide",
    page_icon="💧"
)

st.title("Hydraulic Advance Time Model for Driplines")
st.markdown("""
Professional tool for estimating hydraulic advance time in drip irrigation laterals.

Model inspired by empirical analysis reported in:
DOI: 10.4236/as.2025.1612082
""")

# ------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------
st.sidebar.header("Hydraulic Parameters")

spacing = st.sidebar.number_input(
    "Emitter Spacing (m)",
    min_value=0.05,
    value=0.30,
    step=0.05
)

length = st.sidebar.number_input(
    "Lateral Length (m)",
    min_value=1.0,
    value=150.0,
    step=10.0
)

diameter = st.sidebar.number_input(
    "Internal Diameter (mm)",
    min_value=8.0,
    value=16.0,
    step=1.0
)

flow_dripper = st.sidebar.number_input(
    "Emitter Flow Rate (L/h)",
    min_value=0.5,
    value=1.6,
    step=0.1
)

st.sidebar.markdown("---")
run_sensitivity = st.sidebar.checkbox("Enable Sensitivity Analysis")

# ------------------------------------------------------
# MODEL CALCULATION
# ------------------------------------------------------
TT_full = 0.0912 * (
    (spacing ** 0.7824) *
    (length ** 0.1928) *
    (diameter ** 2)
) / flow_dripper

TT_95 = TT_full / 2

# ------------------------------------------------------
# METRICS DISPLAY
# ------------------------------------------------------
col1, col2 = st.columns(2)

col1.metric("Travel Time – Full Length (min)", f"{TT_full:.2f}")
col2.metric("Travel Time – 95% Length (min)", f"{TT_95:.2f}")

st.markdown("---")

# ------------------------------------------------------
# ADVANCE CURVE SIMULATION
# ------------------------------------------------------
st.subheader("Hydraulic Advance Curve")

relative_time = np.linspace(0, 1, 200)
relative_length = 1 - np.exp(-4 * relative_time)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(relative_time * TT_full, relative_length * length)
ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Distance Reached (m)")
ax.set_title("Simulated Hydraulic Advance Along Dripline")
ax.grid(True)

st.pyplot(fig)

# ------------------------------------------------------
# SENSITIVITY ANALYSIS
# ------------------------------------------------------
if run_sensitivity:
    st.markdown("---")
    st.subheader("Sensitivity Analysis – Diameter Effect")

    diam_range = np.linspace(diameter * 0.6, diameter * 1.4, 50)

    TT_sensitivity = 0.0912 * (
        (spacing ** 0.7824) *
        (length ** 0.1928) *
        (diam_range ** 2)
    ) / flow_dripper

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(diam_range, TT_sensitivity)
    ax2.set_xlabel("Internal Diameter (mm)")
    ax2.set_ylabel("Travel Time (min)")
    ax2.set_title("Sensitivity of Travel Time to Diameter")
    ax2.grid(True)

    st.pyplot(fig2)

# ------------------------------------------------------
# EXPORT SECTION
# ------------------------------------------------------
st.markdown("---")
st.subheader("Export Results")

results_df = pd.DataFrame({
    "Emitter Spacing (m)": [spacing],
    "Length (m)": [length],
    "Diameter (mm)": [diameter],
    "Emitter Flow (L/h)": [flow_dripper],
    "Travel Time Full (min)": [TT_full],
    "Travel Time 95% (min)": [TT_95]
})

st.download_button(
    label="Download Results as CSV",
    data=results_df.to_csv(index=False),
    file_name="hydraulic_advance_results.csv",
    mime="text/csv"
)

# ------------------------------------------------------
# TECHNICAL NOTES
# ------------------------------------------------------
st.markdown("---")
st.subheader("Technical Interpretation")

st.markdown("""
• Travel time increases quadratically with diameter.  
• It increases sub-linearly with lateral length (exponent 0.1928).  
• Higher emitter flow reduces advance time.  
• Spacing influences internal filling dynamics.

This model provides an operational estimate of pressurization advance 
for irrigation design and performance assessment.
""")