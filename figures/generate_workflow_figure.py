"""
Generate the OISA coupling workflow figure for the IEEE BIBM 2026 paper.

Figure layout:
  - Top panel  : Architecture diagram (two models + orchestrator + ISSL signals)
  - Bottom panel: GSimT timeline showing multi-rate scheduling (ODE=6h, ABM=24h)

Output: figures/oisa_workflow.pdf  +  figures/oisa_workflow.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np

# ── Colour palette ──────────────────────────────────────────────────────────
C_ODE        = "#2166ac"   # blue   — Miao2010 ODE
C_ABM        = "#1a9641"   # green  — Sego2020 ABM
C_ORCH       = "#4d4d4d"   # dark grey — orchestrator
C_ISSL       = "#d6604d"   # red-orange — ISSL signals
C_ISSL_BACK  = "#f4a582"   # light orange — reverse signal
C_SOURCE     = "#762a83"   # purple — external source badges
C_TIMELINE   = "#636363"
C_BG_ODE     = "#deebf7"
C_BG_ABM     = "#e5f5e0"
C_BG_ORCH    = "#f0f0f0"

FONT_MAIN = "DejaVu Sans"

# ── Figure setup ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 11))
fig.patch.set_facecolor("white")

gs = fig.add_gridspec(
    2, 1,
    height_ratios=[3.2, 1],
    hspace=0.30,
    left=0.03, right=0.97, top=0.96, bottom=0.03
)
ax_arch     = fig.add_subplot(gs[0])
ax_timeline = fig.add_subplot(gs[1])

for ax in (ax_arch, ax_timeline):
    ax.set_xlim(0, 12)
    ax.set_aspect("equal")
    ax.axis("off")

ax_timeline.set_xlim(0, 12)
ax_timeline.set_ylim(-0.25, 1.80)


# ══════════════════════════════════════════════════════════════════════════════
# PANEL A — Architecture diagram
# ══════════════════════════════════════════════════════════════════════════════

ax_arch.set_xlim(0, 12)
ax_arch.set_ylim(0, 8)

def rounded_box(ax, x, y, w, h, facecolor, edgecolor, lw=1.8, radius=0.18, zorder=2):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=lw, zorder=zorder
    )
    ax.add_patch(box)
    return box

def header_box(ax, x, y, w, h_header, text, facecolor, textcolor="white", fontsize=10):
    box = FancyBboxPatch(
        (x, y), w, h_header,
        boxstyle=f"round,pad=0,rounding_size=0.15",
        facecolor=facecolor, edgecolor="none", zorder=3
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h_header / 2, text,
            ha="center", va="center", fontsize=fontsize, fontweight="bold",
            color=textcolor, zorder=4)

def signal_arrow(ax, x0, y0, x1, y1, color, label, label_side="top", lw=2.0, zorder=5):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw,
            connectionstyle="arc3,rad=0.0",
            mutation_scale=18,
        ),
        zorder=zorder,
    )
    xm = (x0 + x1) / 2
    ym = (y0 + y1) / 2
    dy = 0.24 if label_side == "top" else -0.24
    ax.text(xm, ym + dy, label,
            ha="center", va="center", fontsize=8, color=color,
            fontweight="bold", zorder=zorder + 1,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor=color, linewidth=0.9, alpha=0.92))


# ─── Orchestrator (centre) ───────────────────────────────────────────────────
ox, oy, ow, oh = 4.3, 2.6, 3.4, 3.2
rounded_box(ax_arch, ox, oy, ow, oh, C_BG_ORCH, C_ORCH, lw=2.2)
ax_arch.text(ox + ow / 2, oy + oh - 0.30, "OISA Orchestrator",
             ha="center", va="top", fontsize=12, fontweight="bold",
             color=C_ORCH, zorder=4)

internals = [
    "GSimT clock  (Δt = 6 h)",
    "Causal resolver  (topological DAG)",
    "ISSL router  (signal fan-out)",
    "Watchdog  (divergence_score < 0.15)",
]
for i, txt in enumerate(internals):
    bx = ox + 0.22
    by = oy + oh - 0.70 - i * 0.52
    bw, bh = ow - 0.44, 0.38
    rounded_box(ax_arch, bx, by, bw, bh, "white", C_ORCH, lw=1.1, radius=0.09, zorder=3)
    ax_arch.text(bx + bw / 2, by + bh / 2, txt,
                 ha="center", va="center", fontsize=8.2, color=C_ORCH, zorder=4)


# ─── Miao2010 ODE (left) ─────────────────────────────────────────────────────
mx, my, mw, mh = 0.30, 1.5, 3.30, 4.8
rounded_box(ax_arch, mx, my, mw, mh, C_BG_ODE, C_ODE, lw=2.2)

# Header
header_box(ax_arch, mx, my + mh - 0.58, mw, 0.58,
           "Miao et al. 2010  (ODE)", C_ODE, fontsize=11)

# Source badge
ax_arch.text(mx + mw / 2, my + mh - 0.96,
             "BioModels  BIOMD0000000546",
             ha="center", va="center", fontsize=7.8, color=C_SOURCE,
             fontweight="bold", style="italic",
             bbox=dict(boxstyle="round,pad=0.18", facecolor="#f2e6f9",
                       edgecolor=C_SOURCE, linewidth=1.0, alpha=0.95))

# State variables
ax_arch.text(mx + 0.18, my + mh - 1.40, "State variables  (SBML species):",
             fontsize=8.0, color=C_ODE, fontweight="bold")
svars = [
    ("Ep",  "Uninfected epithelial cells",   "580 000 cells"),
    ("Eps", "Infected epithelial cells",      "0  →  peak ~4×10⁵"),
    ("V",   "Viral load",                     "10³ → ~10⁷ copies / mL"),
]
for i, (sym, desc, val) in enumerate(svars):
    yy = my + mh - 1.80 - i * 0.50
    ax_arch.text(mx + 0.22, yy, sym, fontsize=10, color=C_ODE,
                 fontweight="bold", va="center")
    ax_arch.text(mx + 0.68, yy + 0.10, desc, fontsize=7.8,
                 color="#333333", va="center")
    ax_arch.text(mx + 0.68, yy - 0.14, val, fontsize=7.2,
                 color="#666666", va="center", style="italic")

# Key parameters
ax_arch.text(mx + 0.18, my + 0.98, "Key parameters  (Table 1, Miao 2010):",
             fontsize=8.0, color=C_ODE, fontweight="bold")
params = [
    "β = 10⁻⁶ mL·copies⁻¹·day⁻¹   (infection rate)",
    "π = 100 copies·cell⁻¹·day⁻¹   (viral production)",
    "c_V = 4.2 day⁻¹  |  δ = 0.6 day⁻¹",
    "k_E = 2×10⁻⁵ mL·cell⁻¹·day⁻¹   (CTL killing const.)",
]
for i, p in enumerate(params):
    ax_arch.text(mx + 0.32, my + 0.72 - i * 0.22, p,
                 fontsize=7.4, color="#444444", va="center")

ax_arch.text(mx + mw - 0.18, my + 0.18, "Δt = 6 h",
             ha="right", va="center", fontsize=9.0, color=C_ODE,
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.22", facecolor=C_BG_ODE,
                       edgecolor=C_ODE, linewidth=1.1))

# Emit / Accept labels
ax_arch.text(mx + mw, my + mh * 0.65 + 0.10, "Emit()",
             ha="left", va="bottom", fontsize=7.5, color=C_ISSL,
             fontweight="bold", style="italic")
ax_arch.text(mx + mw, my + mh * 0.35 - 0.10, "Accept()",
             ha="left", va="top", fontsize=7.5, color=C_ISSL_BACK,
             fontweight="bold", style="italic")


# ─── Sego2020 ABM (right) ────────────────────────────────────────────────────
sx, sy, sw, sh = 8.40, 1.5, 3.30, 4.8
rounded_box(ax_arch, sx, sy, sw, sh, C_BG_ABM, C_ABM, lw=2.2)

header_box(ax_arch, sx, sy + sh - 0.58, sw, 0.58,
           "Sego et al. 2020  (ABM)", C_ABM, fontsize=11)

ax_arch.text(sx + sw / 2, sy + sh - 0.96,
             "GitHub  covid-tissue-models  @5b7e42c",
             ha="center", va="center", fontsize=7.8, color=C_SOURCE,
             fontweight="bold", style="italic",
             bbox=dict(boxstyle="round,pad=0.18", facecolor="#f2e6f9",
                       edgecolor=C_SOURCE, linewidth=1.0, alpha=0.95))

ax_arch.text(sx + 0.18, sy + sh - 1.40, "State variables  (immune recruitment):",
             fontsize=8.0, color=C_ABM, fontweight="bold")
avars = [
    ("S",        "Recruitment state variable",    "dS/dt = addRate + ck/delay − …"),
    ("n_immune", "Immune cells in tissue",         "0  →  stochastic seeding"),
    ("total_ck", "Cytokine signal proxy",           "∝ viral load × ir_trans."),
]
for i, (sym, desc, val) in enumerate(avars):
    yy = sy + sh - 1.80 - i * 0.50
    ax_arch.text(sx + 0.22, yy, sym, fontsize=10, color=C_ABM,
                 fontweight="bold", va="center")
    ax_arch.text(sx + 0.82, yy + 0.10, desc, fontsize=7.8,
                 color="#333333", va="center")
    ax_arch.text(sx + 0.82, yy - 0.14, val, fontsize=7.2,
                 color="#666666", va="center", style="italic")

ax_arch.text(sx + 0.18, sy + 0.98, "Parameters  (ViralInfectionVTMModelInputs.py):",
             fontsize=8.0, color=C_ABM, fontweight="bold")
aparams = [
    "addRate  = 1/1200 s⁻¹  ≡  72 day⁻¹",
    "decayRate = 10⁻¹/1200 s⁻¹  ≡  7.2 day⁻¹",
    "ir_transmission_coeff = 0.5",
    "ir_prob_scaling_factor = 0.01",
]
for i, p in enumerate(aparams):
    ax_arch.text(sx + 0.32, sy + 0.72 - i * 0.22, p,
                 fontsize=7.4, color="#444444", va="center")

ax_arch.text(sx + sw - 0.18, sy + 0.18, "Δt = 24 h",
             ha="right", va="center", fontsize=9.0, color=C_ABM,
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.22", facecolor=C_BG_ABM,
                       edgecolor=C_ABM, linewidth=1.1))

ax_arch.text(sx, sy + sh * 0.65 + 0.10, "Accept()",
             ha="right", va="bottom", fontsize=7.5, color=C_ISSL,
             fontweight="bold", style="italic")
ax_arch.text(sx, sy + sh * 0.35 - 0.10, "Emit()",
             ha="right", va="top", fontsize=7.5, color=C_ISSL_BACK,
             fontweight="bold", style="italic")


# ─── ISSL Signals ────────────────────────────────────────────────────────────
# ODE → Orch
signal_arrow(ax_arch,
             mx + mw,  my + mh * 0.65,
             ox,        oy + oh * 0.75,
             C_ISSL, "miao2010.viral_load\n(copies/mL)", label_side="top", lw=2.2)
# Orch → ABM
signal_arrow(ax_arch,
             ox + ow,   oy + oh * 0.75,
             sx,         sy + sh * 0.65,
             C_ISSL, "→ cytokine proxy\n(drives S growth)", label_side="top", lw=2.2)
# ABM → Orch
signal_arrow(ax_arch,
             sx,         sy + sh * 0.35,
             ox + ow,    oy + oh * 0.25,
             C_ISSL_BACK, "sego2020.immune_cell_count\n(n_immune)", label_side="bottom", lw=2.2)
# Orch → ODE
signal_arrow(ax_arch,
             ox,          oy + oh * 0.25,
             mx + mw,     my + mh * 0.35,
             C_ISSL_BACK, "→ T_E_T  (CTL count)\nkilling rate = k_E×Eps×T_E_T", label_side="bottom", lw=2.2)


# ─── Legend ──────────────────────────────────────────────────────────────────
leg_x, leg_y = 4.20, 7.45
ax_arch.text(leg_x, leg_y + 0.30, "ISSL signal direction:", fontsize=8.5,
             color="#222222", fontweight="bold", va="center")
for j, (col, lbl) in enumerate([
    (C_ISSL,      "ODE → ABM :  viral load drives immune recruitment"),
    (C_ISSL_BACK, "ABM → ODE :  immune cells suppress viral replication"),
]):
    yl = leg_y - j * 0.38
    ax_arch.annotate("", xy=(leg_x + 0.42, yl), xytext=(leg_x + 0.08, yl),
                     arrowprops=dict(arrowstyle="-|>", color=col, lw=2.2,
                                     mutation_scale=14), zorder=6)
    ax_arch.text(leg_x + 0.50, yl, lbl, fontsize=8.0, color=col,
                 va="center", fontweight="bold")

# "No modification" banner
ax_arch.text(6.0, 0.45,
             "Zero lines modified in either published model"
             "  —  only  Emit() / Accept()  adapters added  (OISA principle)",
             ha="center", va="center", fontsize=8.5, color="#7f0000",
             fontweight="bold", style="italic",
             bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff5f5",
                       edgecolor="#c0392b", linewidth=1.3, alpha=0.96))

ax_arch.text(0.10, 7.85, "(a)", fontsize=13, fontweight="bold",
             color="#222222", va="top")


# ══════════════════════════════════════════════════════════════════════════════
# PANEL B — GSimT timeline
# ══════════════════════════════════════════════════════════════════════════════

ax_timeline.set_xlim(0, 12)
ax_timeline.set_ylim(-0.30, 1.90)

# Day positions
n_days = 6
day_xs = [1.0 + i * 1.70 for i in range(n_days)]

# Main timeline bar
ax_timeline.axhline(0.85, xmin=0.05, xmax=0.98, color=C_TIMELINE, lw=2.2, zorder=2)

for i, dx in enumerate(day_xs):
    ax_timeline.plot([dx], [0.85], "v", color=C_TIMELINE, ms=10, zorder=3)
    ax_timeline.text(dx, 0.57, f"Day {i}", ha="center", va="top",
                     fontsize=8.5, color=C_TIMELINE, fontweight="bold")
    # ODE ticks (4 per day)
    for q in range(4):
        tx = dx + q * 1.70 / 4
        if tx < day_xs[-1] + 0.15:
            ax_timeline.plot([tx, tx], [0.85, 0.85 + 0.28],
                             color=C_ODE, lw=1.8, zorder=4)
            if q > 0:
                ax_timeline.text(tx, 0.85 + 0.33, f"+{q*6}h",
                                 ha="center", va="bottom", fontsize=6.5, color=C_ODE)
    # ABM tick
    ax_timeline.plot([dx, dx], [0.85, 0.85 - 0.40], color=C_ABM, lw=2.5, zorder=4)
    # ISSL checkpoint dot (daily)
    ax_timeline.plot([dx], [0.85], "o", color=C_ISSL, ms=10, zorder=5,
                     markeredgecolor="white", markeredgewidth=1.5)

# Sub-daily ISSL checkpoints
for i, dx in enumerate(day_xs[:-1]):
    for q in range(1, 4):
        tx = dx + q * 1.70 / 4
        ax_timeline.plot([tx, tx], [0.85, 0.85 + 0.28], color=C_ODE, lw=1.8, zorder=4)
        ax_timeline.plot([tx], [0.85], "o", color=C_ISSL, ms=6, zorder=5,
                         markeredgecolor="white", markeredgewidth=0.8, alpha=0.75)

# Row labels
ax_timeline.text(0.50, 0.85 + 0.18, "ODE  (Δt = 6 h)", ha="right",
                 fontsize=8.5, color=C_ODE, fontweight="bold", va="center")
ax_timeline.text(0.50, 0.85 - 0.25, "ABM  (Δt = 24 h)", ha="right",
                 fontsize=8.5, color=C_ABM, fontweight="bold", va="center")
ax_timeline.text(0.50, 0.85, "ISSL checkpoint", ha="right",
                 fontsize=8.5, color=C_ISSL, fontweight="bold", va="center")

# Causal ordering callout (day 1)
dx1 = day_xs[1]
ax_timeline.annotate(
    "Causal ordering at each 24h boundary:\n"
    "① ABM.emit()  →  ODE.accept()\n"
    "② ODE.step()  →  ODE.emit()\n"
    "③ ABM.accept()  (one-tick delay)",
    xy=(dx1, 0.85 - 0.40), xytext=(dx1 + 0.75, 0.18),
    fontsize=7.5, color="#333333",
    arrowprops=dict(arrowstyle="->", color="#555555", lw=1.2),
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#fafafa",
              edgecolor="#aaaaaa", linewidth=0.9),
    ha="left", va="center", zorder=6
)

# GSimT banner
ax_timeline.text(6.0, 1.70,
                 "GSimT = GCD(6 h, 24 h) = 6 h"
                 "     →     56 ISSL checkpoints per 14-day simulation",
                 ha="center", va="center", fontsize=9.0, color=C_ORCH,
                 fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.35", facecolor=C_BG_ORCH,
                           edgecolor=C_ORCH, linewidth=1.2))

ax_timeline.text(0.10, 1.85, "(b)", fontsize=13, fontweight="bold",
                 color="#222222", va="top")

# ── Save ───────────────────────────────────────────────────────────────────────
import pathlib
out_dir = pathlib.Path(__file__).parent
out_dir.mkdir(exist_ok=True)

fig.savefig(out_dir / "oisa_workflow.pdf", dpi=300, bbox_inches="tight")
fig.savefig(out_dir / "oisa_workflow.png", dpi=200, bbox_inches="tight")
print(f"Saved: {out_dir / 'oisa_workflow.pdf'}")
print(f"Saved: {out_dir / 'oisa_workflow.png'}")
