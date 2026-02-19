import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------
st.set_page_config(
    page_title="Hydraulic Advance Time – Professional Tool",
    layout="wide",
    page_icon="💧"
)

st.title("Hydraulic Advance Time Model for Driplines")

st.markdown("""
Professional hydraulic advance time estimator for drip irrigation laterals.

Model inspired by empirical findings reported in:  
🔗 [DOI: 10.4236/as.2025.1612082](https://www.scirp.org/journal/paperinformation?paperid=148372)
""")

# ------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------
st.sidebar.header("Hydraulic Parameters")

spacing = st.sidebar.number_input("Emitter Spacing (m)", 0.05, 1.0, 0.30, 0.05)
length = st.sidebar.number_input("Reference Lateral Length (m)", 1.0, 500.0, 150.0, 10.0)
diameter = st.sidebar.number_input("Internal Diameter (mm)", 8.0, 32.0, 16.0, 1.0)
flow_dripper = st.sidebar.number_input("Emitter Flow Rate (L/h)", 0.5, 8.0, 1.6, 0.1)

# ------------------------------------------------------
# MODEL FUNCTION
# ------------------------------------------------------
def travel_time(spacing, length, diameter, flow_dripper):
    return 0.0912 * (
        (spacing ** 0.7824) *
        (length ** 0.1928) *
        (diameter ** 2)
    ) / flow_dripper

# ------------------------------------------------------
# MAIN CALCULATION
# ------------------------------------------------------
TT_full = travel_time(spacing, length, diameter, flow_dripper)
TT_95 = TT_full / 2

col1, col2 = st.columns(2)
col1.metric("Travel Time – Full Length (min)", f"{TT_full:.2f}")
col2.metric("Travel Time – 95% Length (min)", f"{TT_95:.2f}")

st.markdown("---")

# ======================================================
# GRAPH 1: Travel Time vs Lateral Length
# ======================================================
st.subheader("1️⃣ Travel Time vs Lateral Length")

length_range = np.linspace(10, 300, 200)
TT_values = travel_time(spacing, length_range, diameter, flow_dripper)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=length_range,
    y=TT_values,
    mode='lines',
    name="Travel Time",
    line=dict(width=4)
))

fig1.update_layout(
    xaxis_title="Lateral Length (m)",
    yaxis_title="Travel Time (min)",
    template="plotly_white",
    title="Advance Time as Function of Lateral Length",
    height=500
)

st.plotly_chart(fig1, use_container_width=True)


# ======================================================
# GRAPH 2: Lateral Length vs Inlet Flow Velocity
# ======================================================
st.subheader("2️⃣ Lateral Length vs Inlet Flow Velocity")

# Convert diameter to meters
diameter_m = diameter / 1000

# Cross-sectional area (m²)
area = np.pi * (diameter_m / 2) ** 2

# Convert emitter flow to m³/s
flow_m3s = flow_dripper / 1000 / 3600

# Number of emitters for each length
emitters = length_range / spacing

# Inlet flow for each length
Q_inlet = emitters * flow_m3s

# Velocity at inlet
velocity = Q_inlet / area

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=length_range,
    y=velocity,
    mode='lines',
    name="Inlet Velocity",
    line=dict(width=4)
))

fig2.update_layout(
    xaxis_title="Lateral Length (m)",
    yaxis_title="Inlet Flow Velocity (m/s)",
    template="plotly_white",
    title="Inlet Velocity as Function of Lateral Length",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------
# TECHNICAL NOTES
# ------------------------------------------------------
st.markdown("---")
st.subheader("Engineering Interpretation")

st.markdown("""
• Travel time increases sub-linearly with lateral length.  
• Travel time increases quadratically with diameter.  
• Higher emitter flow reduces advance time.  
• Velocity is estimated assuming steady internal pipe flow.

This tool provides operational support for irrigation system design,
pressurization analysis, and performance evaluation.
""")