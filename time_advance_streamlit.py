# ==========================================================
# HYDRAULIC ADVANCE ANALYSIS – EMPIRICAL + SEGMENT MODEL
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------

st.set_page_config(page_title="Hydraulic Advance Analysis", layout="wide")

st.title("Hydraulic Advance Analysis for Driplines")

st.markdown("""
Empirical model reference:

🔗 DOI: [10.4236/as.2025.1612082](https://www.scirp.org/journal/paperinformation?paperid=148372)
""")

# ----------------------------------------------------------
# SIDEBAR INPUTS
# ----------------------------------------------------------

st.sidebar.header("Input Parameters")

q = st.sidebar.number_input("Emitter flow rate (L/h)", 0.1, 10.0, 1.0)
S = st.sidebar.number_input("Emitter spacing (m)", 0.05, 2.0, 0.5)
L = st.sidebar.number_input("Dripline length (m)", 10.0, 1000.0, 150.0)
dia = st.sidebar.number_input("Internal diameter (mm)", 8.0, 40.0, 20.2)

# ----------------------------------------------------------
# EMPIRICAL TRAVEL TIME
# ----------------------------------------------------------

TT_empirical = 0.0912 * (
    (S ** 0.7824) *
    (L ** 0.1928) *
    (dia ** 2)
) / q

TT_95_empirical = TT_empirical / 2

# ----------------------------------------------------------
# SEGMENTED HYDRAULIC MODEL
# ----------------------------------------------------------

outlets = int(L / S)

df = pd.DataFrame(index=range(1, outlets + 1))

df["outlets"] = df.index
df["long_acum"] = df.index * S

Q_total = outlets * q
df["q_tramo"] = Q_total - df.index * q

Area = np.pi * (dia / 2000)**2

# velocity (m/s)
df["v_tramo"] = df["q_tramo"] / 1000 / 3600 / Area

# avoid zero velocity in last segment
df["v_tramo"] = df["v_tramo"].replace(0, np.nan)
df["v_tramo"] = df["v_tramo"].fillna(method="ffill")

# time per segment (seconds)
df["t_tramo"] = S / df["v_tramo"]

# ----------------------------------------------------------
# SCALE TIME TO MATCH EMPIRICAL MODEL
# ----------------------------------------------------------

TT_hydraulic_minutes = df["t_tramo"].sum() / 60

scale_factor = TT_empirical / TT_hydraulic_minutes

df["t_tramo"] = df["t_tramo"] * scale_factor

df["t_acum"] = df["t_tramo"].cumsum() / 60

travel_time = round(df["t_acum"].iloc[-1], 4)

index_95 = int(outlets * 0.95)
travel_time_95 = round(df.loc[index_95, "t_acum"], 4)

# ----------------------------------------------------------
# HEAD LOSS CALCULATION
# ----------------------------------------------------------

df["headloss"] = 1.131 * 10**9 * (df["q_tramo"] / 1000 / 140)**1.852 * S * dia**-4.872
df["HL_acum"] = df["headloss"].cumsum()

HF = round(df["headloss"].sum(), 3)

# ----------------------------------------------------------
# DISPLAY METRICS
# ----------------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Travel Time (100%) [min]", f"{travel_time:.3f}")
col2.metric("Travel Time (95%) [min]", f"{travel_time_95:.3f}")
col3.metric("Total Head Loss [m]", f"{HF:.3f}")

# ----------------------------------------------------------
# GRAPHS (IDENTICAL STYLE TO YOUR EXAMPLE)
# ----------------------------------------------------------

fig = plt.figure(figsize=(16, 6))

def configure_axes(ax):
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(True)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.tick_params(labelsize=12)

# ---------------- GRAPH A ----------------

ax1 = fig.add_subplot(131)
configure_axes(ax1)

color = 'tab:red'
ax1.set_xlabel('Length of pipe (m)', fontsize=12)
ax1.set_ylabel('Accumulated headloss (m)', color=color, fontsize=12)
ax1.plot(df['long_acum'], df['HL_acum'], color=color, linestyle='--')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_title('(A)', fontsize=14)

ax2 = ax1.twinx()
configure_axes(ax2)
color = 'tab:blue'
ax2.set_ylabel('Travel time (min)', color=color, fontsize=12)
ax2.scatter(df['long_acum'], df['t_acum'], color=color, s=10)
ax2.tick_params(axis='y', labelcolor=color)

# ---------------- GRAPH B ----------------

ax1 = fig.add_subplot(132)
configure_axes(ax1)

color = 'tab:red'
ax1.set_xlabel('Length of pipe (m)', fontsize=12)
ax1.set_ylabel('Velocity (m/s)', color=color, fontsize=12)
ax1.plot(df['long_acum'], df['v_tramo'], color=color, linestyle='--')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_title('(B)', fontsize=14)

ax2 = ax1.twinx()
configure_axes(ax2)
color = 'tab:blue'
ax2.set_ylabel('Travel time (min)', color=color, fontsize=12)
ax2.scatter(df['long_acum'], df['t_acum'], color=color, s=10)
ax2.tick_params(axis='y', labelcolor=color)

# ---------------- GRAPH C ----------------

a = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.00]
b = [0.00, 0.47, 0.25, 0.13, 0.07, 0.04, 0.02, 0.01, 0.01, 0.00, 0.00]
c = [0, 0.47, 0.71, 0.85, 0.92, 0.96, 0.98, 0.99, 0.99, 1, 1]

ax1 = fig.add_subplot(133)
configure_axes(ax1)

color = 'tab:red'
ax1.set_xlabel('Relative advance time', fontsize=12)
ax1.set_ylabel('Frequency', color=color, fontsize=12)
ax1.plot(a, b, color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_title('(C)', fontsize=14)

ax2 = ax1.twinx()
configure_axes(ax2)
color = 'tab:blue'
ax2.set_ylabel('Cumulative relative length', color=color, fontsize=12)
ax2.plot(a, c, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()

st.pyplot(fig)

# ----------------------------------------------------------
# EXPORT OPTION
# ----------------------------------------------------------

st.download_button(
    label="Download Results CSV",
    data=df.to_csv(index=False),
    file_name="hydraulic_advance_results.csv",
    mime="text/csv"
)
st.markdown("Guevara Rodríguez, G. and Watson Hernandez, F.(2026)")
