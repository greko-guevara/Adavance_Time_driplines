import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------
st.set_page_config(layout="wide", page_title="Hydraulic Advance Professional Tool")

st.title("Hydraulic Advance Analysis for Driplines")

st.markdown("""
Professional hydraulic advance and energy dissipation model.

Inspired by empirical findings reported in:  
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
# HYDRAULIC MODEL
# ------------------------------------------------------

diameter = diameter_mm / 1000
area = np.pi * (diameter / 2)**2
flow_m3s = flow_lph / 1000 / 3600

segments = 100
dx = length / segments

long_acum = []
HL_acum = []
v_tramo = []
t_acum = []

g = 9.81
f = 0.03  # assumed friction factor
Q = (length/spacing) * flow_m3s

headloss_total = 0
time_total = 0

for i in range(segments):
    x = dx * (i + 1)
    emitters_remaining = (length - x) / spacing
    Q_segment = emitters_remaining * flow_m3s
    v = Q_segment / area

    hf = f * (dx/diameter) * (v**2)/(2*g)

    dt = dx / max(v, 1e-6)

    headloss_total += hf
    time_total += dt

    long_acum.append(x)
    HL_acum.append(headloss_total)
    v_tramo.append(v)
    t_acum.append(time_total/60)

df = pd.DataFrame({
    "long_acum": long_acum,
    "HL_acum": HL_acum,
    "v_tramo": v_tramo,
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
    ax.tick_params(labelsize=12)

# GRAPH A
ax1 = fig.add_subplot(131)
configurar_ejes(ax1)

ax1.set_xlabel('Length of pipe (m)')
ax1.set_ylabel('Accumulated headloss (m)', color='red')
ax1.plot(df['long_acum'], df['HL_acum'], 'r--', label="Headloss")
ax1.tick_params(axis='y', labelcolor='red')
ax1.set_title('(A)')

ax2 = ax1.twinx()
configurar_ejes(ax2)
ax2.set_ylabel('Travel time (min)', color='blue')
ax2.scatter(df['long_acum'], df['t_acum'], color='blue', s=10)
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
ax2.scatter(df['long_acum'], df['t_acum'], color='blue', s=10)
ax2.tick_params(axis='y', labelcolor='blue')

# GRAPH C
a = np.linspace(0,1,100)
b = np.exp(-4*a)
c = 1 - b

ax1 = fig.add_subplot(133)
configurar_ejes(ax1)

ax1.set_xlabel('Relative advance time')
ax1.set_ylabel('Relative length of dripline', color='red')
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
st.metric("Total Travel Time (min)", f"{df['t_acum'].iloc[-1]:.2f}")
st.metric("Total Headloss (m)", f"{df['HL_acum'].iloc[-1]:.3f}")
