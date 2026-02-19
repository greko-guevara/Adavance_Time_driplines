import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------
st.set_page_config(layout="wide", page_title="Hydraulic Advance Empirical Model")

st.title("Hydraulic Advance Analysis for Driplines")

st.markdown("""
Empirical advance time model based on:

🔗 [DOI: 10.4236/as.2025.1612082](https://www.scirp.org/journal/paperinformation?paperid=148372)
""")

# ------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------
st.sidebar.header("Hydraulic Parameters")

spacing = st.sidebar.number_input("Emitter Spacing (m)", 0.05, 1.0, 0.30)
length = st.sidebar.number_input("Lateral Length (m)", 10.0, 500.0, 150.0)
diameter_mm = st.sidebar.number_input("Internal Diameter (mm)", 8.0, 32.0, 16.0)
flow_lph = st.sidebar.number_input("Emitter Flow (L/h)", 0.5, 8.0, 1.6)

# ------------------------------------------------------
# EMPIRICAL TRAVEL TIME CALCULATION
# ------------------------------------------------------
TT_full = 0.0912 * (
    (spacing ** 0.7824) *
    (length ** 0.1928) *
    (diameter_mm ** 2)
) / flow_lph

TT_95 = TT_full / 2

# ------------------------------------------------------
# VELOCITY CALCULATION (PHYSICAL, NOT FOR TIME)
# ------------------------------------------------------
diameter_m = diameter_mm / 1000
area = np.pi * (diameter_m / 2) ** 2
flow_m3s = flow_lph / 1000 / 3600

emitters = length / spacing
Q_inlet = emitters * flow_m3s
velocity_inlet = Q_inlet / area

# ------------------------------------------------------
# BUILD ADVANCE CURVE BASED ON EMPIRICAL TIME
# ------------------------------------------------------
segments = 100
long_acum = np.linspace(0, length, segments)

relative_length = long_acum / length
t_acum = TT_full * (1 - np.exp(-4 * relative_length))

# simple smooth accumulated headloss trend for visualization
HL_acum = 5 * (1 - np.exp(-3 * relative_length))

df = pd.DataFrame({
    "long_acum": long_acum,
    "HL_acum": HL_acum,
    "v_tramo": np.full_like(long_acum, velocity_inlet),
    "t_acum": t_acum
})

# ------------------------------------------------------
# GRAPHICS
# ------------------------------------------------------
fig = plt.figure(figsize=(16, 6))

def configurar_ejes(ax):
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.tick_params(labelsize=11)

# GRAPH A
ax1 = fig.add_subplot(131)
configurar_ejes(ax1)
ax1.set_xlabel('Length of pipe (m)')
ax1.set_ylabel('Accumulated headloss (m)', color='red')
ax1.plot(df['long_acum'], df['HL_acum'], 'r--')
ax1.tick_params(axis='y', labelcolor='red')
ax1.set_title('(A)')

ax2 = ax1.twinx()
configurar_ejes(ax2)
ax2.set_ylabel('Travel time (min)', color='blue')
ax2.plot(df['long_acum'], df['t_acum'], 'b')
ax2.tick_params(axis='y', labelcolor='blue')

# GRAPH B
ax1 = fig.add_subplot(132)
configurar_ejes(ax1)
ax1.set_xlabel('Length of pipe (m)')
ax1.set_ylabel('Velocity (m/s)', color='red')
ax1.plot(df['long_acum'], df['v_tramo'], 'r--')
ax1.tick_params(axis='y', labelcolor='red')
ax1.set_title('(B)')

ax2 = ax1.twinx()
configurar_ejes(ax2)
ax2.set_ylabel('Travel time (min)', color='blue')
ax2.plot(df['long_acum'], df['t_acum'], 'b')
ax2.tick_params(axis='y', labelcolor='blue')

# GRAPH C
a = np.linspace(0, 1, 100)
b = np.exp(-4 * a)
c = 1 - b

ax1 = fig.add_subplot(133)
configurar_ejes(ax1)
ax1.set_xlabel('Relative advance time')
ax1.set_ylabel('Frequency', color='red')
ax1.plot(a, b, 'r')
ax1.set_title('(C)')

ax2 = ax1.twinx()
configurar_ejes(ax2)
ax2.set_ylabel('Cumulative relative length', color='blue')
ax2.plot(a, c, 'b')

plt.tight_layout()
plt.savefig("hydraulic_advance_figure.png", dpi=300, bbox_inches='tight')

st.pyplot(fig)

# ------------------------------------------------------
# RESULTS
# ------------------------------------------------------
st.metric("Travel Time - Full Length (min)", f"{TT_full:.2f}")
st.metric("Travel Time - 95% Length (min)", f"{TT_95:.2f}")
st.metric("Estimated Inlet Velocity (m/s)", f"{velocity_inlet:.3f}")
