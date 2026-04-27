"""
Generate the OISA coupling workflow figure for the IEEE BIBM 2026 paper.

Panel (a) — Architecture: three horizontally aligned boxes of equal height
            (ODE | Orchestrator | ABM). Forward ISSL signals flow in a
            clean upper corridor (ODE → Orch → ABM). Return ISSL signals
            flow in a clean lower corridor (ABM → Orch → ODE). No arrow
            crosses box interiors; all labels sit in the gap corridors.

Panel (b) — GSimT multi-rate timeline: ODE ticks every 6 h (upward lines),
            ABM ticks every 24 h (downward triangles), ISSL checkpoint
            markers on the main axis at every ODE tick.

Design targets:
  - Readable at IEEE 2-column full-page width (~7 in typeset).
  - No overlapping glyphs. No text clipped by arrows.
  - Parameter detail lives in paper tables, not in the figure; the boxes
    show only the information required to interpret the signal flow.
"""

from __future__ import annotations

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ── Palette (ColorBrewer-derived, colour-blind safe) ────────────────────────
C_ODE       = "#2166ac"
C_ABM       = "#1a9641"
C_ORCH      = "#4d4d4d"
C_ISSL_FWD  = "#b2182b"
C_ISSL_RET  = "#e08214"
C_SOURCE    = "#762a83"
C_TIMELINE  = "#525252"
C_BG_ODE    = "#deebf7"
C_BG_ABM    = "#e5f5e0"
C_BG_ORCH   = "#f0f0f0"
C_BANNER    = "#7f0000"
C_BANNER_BG = "#fff5f5"

FIG_W, FIG_H = 14.0, 10.0

# ════════════════════════════════════════════════════════════════════════════
# Figure scaffold
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("white")

gs = fig.add_gridspec(
    2, 1,
    height_ratios=[3.0, 1.0],
    hspace=0.15,
    left=0.02, right=0.98, top=0.98, bottom=0.03,
)
ax_arch = fig.add_subplot(gs[0])
ax_tl   = fig.add_subplot(gs[1])
for ax in (ax_arch, ax_tl):
    ax.set_aspect("equal")
    ax.axis("off")


# ── helpers ─────────────────────────────────────────────────────────────────
def rbox(ax, x, y, w, h, fc, ec, lw=1.6, r=0.18, z=2):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z,
    )
    ax.add_patch(p)
    return p


def header_bar(ax, x, y, w, h, text, fc, fs=11.5):
    rbox(ax, x, y, w, h, fc, "none", lw=0, r=0.16, z=3)
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fs, fontweight="bold",
            color="white", zorder=4)


def arrow(ax, p0, p1, color, lw=2.4, z=5, style="-|>"):
    a = FancyArrowPatch(
        p0, p1,
        arrowstyle=style, mutation_scale=20, lw=lw, color=color,
        connectionstyle="arc3,rad=0.0", zorder=z,
    )
    ax.add_patch(a)


def arrow_label(ax, p0, p1, text, color, lift=0.0, z=7):
    """Place a white-filled, colour-bordered label at the midpoint of an
    arrow, lifted perpendicular to the arrow by `lift` axis units."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    ax.text(mx, my + lift, text,
            ha="center", va="center", fontsize=8.4, color=color,
            fontweight="bold", zorder=z,
            bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                      edgecolor=color, linewidth=1.1))


# ════════════════════════════════════════════════════════════════════════════
# PANEL (a) — Architecture
# ════════════════════════════════════════════════════════════════════════════
ax_arch.set_xlim(0, 14)
ax_arch.set_ylim(0, 10)

ax_arch.text(0.12, 9.80, "(a)", fontsize=14.5, fontweight="bold",
             color="#222222", va="top")

# Three boxes, same y-range, wide gaps to host signal corridors
BOX_Y, BOX_H = 3.20, 4.60            # boxes span y = 3.20 .. 7.80
ODE_X, ODE_W = 0.40, 3.60
OR_X,  OR_W  = 5.30, 3.40
ABM_X, ABM_W = 10.00, 3.60

# Signal corridors (above and below boxes)
Y_FWD = 8.40     # forward  (ODE → Orch → ABM)
Y_RET = 2.20     # return   (ABM → Orch → ODE)

# ── ODE box ─────────────────────────────────────────────────────────────────
rbox(ax_arch, ODE_X, BOX_Y, ODE_W, BOX_H, C_BG_ODE, C_ODE, lw=2.4)
header_bar(ax_arch, ODE_X, BOX_Y + BOX_H - 0.70, ODE_W, 0.70,
           "Miao 2010  —  ODE", C_ODE, fs=13.0)
# Δt pill: small coloured tab overlapping the header bar's bottom-right
ax_arch.text(ODE_X + ODE_W - 0.15, BOX_Y + BOX_H - 0.70,
             "Δt = 6 h", ha="right", va="center", fontsize=8.6,
             color="white", fontweight="bold", zorder=5,
             bbox=dict(boxstyle="round,pad=0.20", facecolor=C_ODE,
                       edgecolor="white", linewidth=1.2))

ax_arch.text(ODE_X + ODE_W / 2, BOX_Y + BOX_H - 1.05,
             "BioModels  BIOMD0000000546",
             ha="center", va="center", fontsize=7.8, color=C_SOURCE,
             fontweight="bold", style="italic",
             bbox=dict(boxstyle="round,pad=0.20", facecolor="#f5ecfb",
                       edgecolor=C_SOURCE, linewidth=1.0))

ax_arch.text(ODE_X + 0.25, BOX_Y + BOX_H - 1.75,
             "State variables:",
             fontsize=9.0, color=C_ODE, fontweight="bold")
for i, (sym, desc) in enumerate([
    ("Ep",  "uninfected epi. cells"),
    ("Eps", "infected epi. cells"),
    ("V",   "viral load (copies/mL)"),
]):
    yy = BOX_Y + BOX_H - 2.15 - i * 0.40
    ax_arch.text(ODE_X + 0.30, yy, sym, fontsize=10.0, color=C_ODE,
                 fontweight="bold", va="center")
    ax_arch.text(ODE_X + 1.10, yy, desc, fontsize=8.2,
                 color="#222222", va="center")

ax_arch.text(ODE_X + 0.25, BOX_Y + 0.80,
             "Coupling I/O:", fontsize=9.0, color=C_ODE,
             fontweight="bold")
ax_arch.text(ODE_X + 0.30, BOX_Y + 0.48,
             "Emit   :  V  (viral load)",
             fontsize=8.2, color="#222222", va="center",
             family="DejaVu Sans Mono")
ax_arch.text(ODE_X + 0.30, BOX_Y + 0.20,
             "Accept :  T_E_T  (CTL)",
             fontsize=8.2, color="#222222", va="center",
             family="DejaVu Sans Mono")

# ── ABM box ─────────────────────────────────────────────────────────────────
rbox(ax_arch, ABM_X, BOX_Y, ABM_W, BOX_H, C_BG_ABM, C_ABM, lw=2.4)
header_bar(ax_arch, ABM_X, BOX_Y + BOX_H - 0.70, ABM_W, 0.70,
           "Sego 2020  —  ABM", C_ABM, fs=13.0)
ax_arch.text(ABM_X + ABM_W - 0.15, BOX_Y + BOX_H - 0.70,
             "Δt = 24 h", ha="right", va="center", fontsize=8.6,
             color="white", fontweight="bold", zorder=5,
             bbox=dict(boxstyle="round,pad=0.20", facecolor=C_ABM,
                       edgecolor="white", linewidth=1.2))

ax_arch.text(ABM_X + ABM_W / 2, BOX_Y + BOX_H - 1.05,
             "ViralInfectionVTM  @5b7e42c",
             ha="center", va="center", fontsize=7.8, color=C_SOURCE,
             fontweight="bold", style="italic",
             bbox=dict(boxstyle="round,pad=0.20", facecolor="#f5ecfb",
                       edgecolor=C_SOURCE, linewidth=1.0))

ax_arch.text(ABM_X + 0.25, BOX_Y + BOX_H - 1.75,
             "State variables:",
             fontsize=9.0, color=C_ABM, fontweight="bold")
for i, (sym, desc) in enumerate([
    ("n_immune", "tissue immune cells"),
    ("total_ck", "cytokine integral"),
    ("S",        "recruitment var."),
]):
    yy = BOX_Y + BOX_H - 2.15 - i * 0.40
    ax_arch.text(ABM_X + 0.30, yy, sym, fontsize=10.0, color=C_ABM,
                 fontweight="bold", va="center")
    ax_arch.text(ABM_X + 1.75, yy, desc, fontsize=8.2,
                 color="#222222", va="center")

ax_arch.text(ABM_X + 0.25, BOX_Y + 0.80,
             "Coupling I/O:", fontsize=9.0, color=C_ABM,
             fontweight="bold")
ax_arch.text(ABM_X + 0.30, BOX_Y + 0.48,
             "Accept :  cytokine (∝ V)",
             fontsize=8.2, color="#222222", va="center",
             family="DejaVu Sans Mono")
ax_arch.text(ABM_X + 0.30, BOX_Y + 0.20,
             "Emit   :  n_immune",
             fontsize=8.2, color="#222222", va="center",
             family="DejaVu Sans Mono")

# ── Orchestrator (centre) ───────────────────────────────────────────────────
rbox(ax_arch, OR_X, BOX_Y, OR_W, BOX_H, C_BG_ORCH, C_ORCH, lw=2.6)
header_bar(ax_arch, OR_X, BOX_Y + BOX_H - 0.70, OR_W, 0.70,
           "OISA  Orchestrator", C_ORCH, fs=12.2)

internals = [
    "GSimT clock   (Δt = 6 h)",
    "Causal resolver   (DAG)",
    "ISSL router",
    "Watchdog   (div. < 0.15)",
]
n = len(internals)
top_of_internals = BOX_Y + BOX_H - 0.95
cell_h = 0.46
spacing = 0.06
for i, txt in enumerate(internals):
    by = top_of_internals - (i + 1) * cell_h - i * spacing
    bx = OR_X + 0.25
    bw = OR_W - 0.50
    rbox(ax_arch, bx, by, bw, cell_h, "white", C_ORCH, lw=1.0, r=0.08, z=3)
    ax_arch.text(bx + bw / 2, by + cell_h / 2, txt,
                 ha="center", va="center", fontsize=8.8,
                 color=C_ORCH, zorder=4)

# ── Signal corridors ────────────────────────────────────────────────────────
# Upward stubs (boxes → forward corridor)
arrow(ax_arch, (ODE_X + ODE_W * 0.60, BOX_Y + BOX_H),
      (ODE_X + ODE_W * 0.60, Y_FWD - 0.05),
      C_ISSL_FWD, lw=2.4, style="-")
arrow(ax_arch, (OR_X + OR_W * 0.40, BOX_Y + BOX_H),
      (OR_X + OR_W * 0.40, Y_FWD - 0.05),
      C_ISSL_FWD, lw=2.4, style="-")
arrow(ax_arch, (OR_X + OR_W * 0.60, BOX_Y + BOX_H),
      (OR_X + OR_W * 0.60, Y_FWD - 0.05),
      C_ISSL_FWD, lw=2.4, style="-")
arrow(ax_arch, (ABM_X + ABM_W * 0.40, BOX_Y + BOX_H),
      (ABM_X + ABM_W * 0.40, Y_FWD - 0.05),
      C_ISSL_FWD, lw=2.4, style="-")

# Forward horizontal segments
p_ode_up  = (ODE_X + ODE_W * 0.60, Y_FWD)
p_orch_L  = (OR_X  + OR_W  * 0.40, Y_FWD)
p_orch_R  = (OR_X  + OR_W  * 0.60, Y_FWD)
p_abm_up  = (ABM_X + ABM_W * 0.40, Y_FWD)

arrow(ax_arch, p_ode_up, p_orch_L, C_ISSL_FWD, lw=2.6)
arrow_label(ax_arch, p_ode_up, p_orch_L,
            "miao2010.viral_load\n(copies / mL)",
            C_ISSL_FWD, lift=0.55)

arrow(ax_arch, p_orch_R, p_abm_up, C_ISSL_FWD, lw=2.6)
arrow_label(ax_arch, p_orch_R, p_abm_up,
            "→ cytokine proxy\n(drives S)",
            C_ISSL_FWD, lift=0.55)

# Downward stubs (boxes → return corridor)
arrow(ax_arch, (ABM_X + ABM_W * 0.60, BOX_Y),
      (ABM_X + ABM_W * 0.60, Y_RET + 0.05),
      C_ISSL_RET, lw=2.4, style="-")
arrow(ax_arch, (OR_X + OR_W * 0.60, BOX_Y),
      (OR_X + OR_W * 0.60, Y_RET + 0.05),
      C_ISSL_RET, lw=2.4, style="-")
arrow(ax_arch, (OR_X + OR_W * 0.40, BOX_Y),
      (OR_X + OR_W * 0.40, Y_RET + 0.05),
      C_ISSL_RET, lw=2.4, style="-")
arrow(ax_arch, (ODE_X + ODE_W * 0.40, BOX_Y),
      (ODE_X + ODE_W * 0.40, Y_RET + 0.05),
      C_ISSL_RET, lw=2.4, style="-")

p_abm_dn = (ABM_X + ABM_W * 0.60, Y_RET)
p_orch_R_dn = (OR_X + OR_W * 0.60, Y_RET)
p_orch_L_dn = (OR_X + OR_W * 0.40, Y_RET)
p_ode_dn = (ODE_X + ODE_W * 0.40, Y_RET)

arrow(ax_arch, p_abm_dn, p_orch_R_dn, C_ISSL_RET, lw=2.6)
arrow_label(ax_arch, p_abm_dn, p_orch_R_dn,
            "sego2020.immune_cell_count\n(n_immune)",
            C_ISSL_RET, lift=-0.55)

arrow(ax_arch, p_orch_L_dn, p_ode_dn, C_ISSL_RET, lw=2.6)
arrow_label(ax_arch, p_orch_L_dn, p_ode_dn,
            "→ T_E_T\n(CTL count)",
            C_ISSL_RET, lift=-0.55)

# Corridor labels — compact badges placed inside the corridor, away
# from the arrow lanes so they don't collide with arrow glyphs.
ax_arch.text(13.70, Y_FWD, "ISSL\nforward",
             ha="center", va="center", fontsize=8.4,
             color=C_ISSL_FWD, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                       edgecolor=C_ISSL_FWD, linewidth=1.0))
ax_arch.text(0.30, Y_RET, "ISSL\nreturn",
             ha="center", va="center", fontsize=8.4,
             color=C_ISSL_RET, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                       edgecolor=C_ISSL_RET, linewidth=1.0))

# ── "Zero modification" banner ──────────────────────────────────────────────
ax_arch.text(7.0, 0.85,
             "Zero lines modified in either published model — "
             "only  Emit()  /  Accept()  adapters added   (OISA principle)",
             ha="center", va="center", fontsize=9.6, color=C_BANNER,
             fontweight="bold", style="italic",
             bbox=dict(boxstyle="round,pad=0.40", facecolor=C_BANNER_BG,
                       edgecolor="#c0392b", linewidth=1.4))


# ════════════════════════════════════════════════════════════════════════════
# PANEL (b) — GSimT timeline
# ════════════════════════════════════════════════════════════════════════════
ax_tl.set_xlim(0, 14)
ax_tl.set_ylim(-0.40, 2.60)

ax_tl.text(0.12, 2.45, "(b)", fontsize=14.5, fontweight="bold",
           color="#222222", va="top")

# Banner
ax_tl.text(7.0, 2.35,
           "GSimT = GCD(6 h, 24 h) = 6 h      →      "
           "56 ISSL checkpoints over a 14-day simulation",
           ha="center", va="center", fontsize=10.0, color=C_ORCH,
           fontweight="bold",
           bbox=dict(boxstyle="round,pad=0.32", facecolor=C_BG_ORCH,
                     edgecolor=C_ORCH, linewidth=1.2))

Y_ODE  = 1.55
Y_AXIS = 1.05
Y_ABM  = 0.55

ax_tl.text(1.05, Y_ODE, "ODE   (Δt = 6 h)",  ha="right", va="center",
           fontsize=9.4, color=C_ODE, fontweight="bold")
ax_tl.text(1.05, Y_AXIS, "ISSL checkpoint",  ha="right", va="center",
           fontsize=9.4, color=C_ISSL_FWD, fontweight="bold")
ax_tl.text(1.05, Y_ABM, "ABM   (Δt = 24 h)", ha="right", va="center",
           fontsize=9.4, color=C_ABM, fontweight="bold")

n_days = 7
day_xs = [1.35 + i * 1.65 for i in range(n_days)]

# Main axis
ax_tl.plot([day_xs[0] - 0.30, day_xs[-1] + 0.30],
           [Y_AXIS, Y_AXIS], color=C_TIMELINE, lw=2.0, zorder=2)

for i, dx in enumerate(day_xs):
    # Day label (below ABM row)
    ax_tl.text(dx, Y_ABM - 0.30, f"Day {i}", ha="center", va="top",
               fontsize=8.8, color=C_TIMELINE, fontweight="bold")

    # ABM tick (every 24 h)
    ax_tl.plot([dx, dx], [Y_AXIS, Y_ABM + 0.02], color=C_ABM, lw=2.6,
               zorder=4, solid_capstyle="round")
    ax_tl.plot([dx], [Y_ABM + 0.02], "v", color=C_ABM, ms=10, zorder=5,
               markeredgecolor="white", markeredgewidth=1.2)

    # ODE ticks (every 6 h) within this day, plus ISSL dots
    if i < n_days - 1:
        for q in range(4):
            tx = dx + q * 1.65 / 4
            ax_tl.plot([tx, tx], [Y_AXIS, Y_ODE - 0.02], color=C_ODE,
                       lw=1.8, zorder=4, solid_capstyle="round")
            ax_tl.plot([tx], [Y_ODE - 0.02], "^", color=C_ODE, ms=7,
                       zorder=5, markeredgecolor="white",
                       markeredgewidth=0.9)
            # ISSL checkpoint (larger at day boundary)
            ms = 10 if q == 0 else 6.5
            ax_tl.plot([tx], [Y_AXIS], "o", color=C_ISSL_FWD, ms=ms,
                       zorder=6, markeredgecolor="white",
                       markeredgewidth=1.2)
            if q > 0:
                ax_tl.text(tx, Y_ODE + 0.12, f"+{q*6}h",
                           ha="center", va="bottom",
                           fontsize=6.6, color=C_ODE)
    else:
        # Final day: single ISSL dot
        ax_tl.plot([dx], [Y_AXIS], "o", color=C_ISSL_FWD, ms=10,
                   zorder=6, markeredgecolor="white", markeredgewidth=1.2)

# Causal ordering callout — anchor on Day 2, float to the right under Days 4-6
ax_tl.annotate(
    "Causal ordering at each 24-h boundary:\n"
    "①  ABM.emit()     →  ODE.accept()\n"
    "②  ODE.step()     →  ODE.emit()\n"
    "③  ABM.accept()   (one-tick delay)",
    xy=(day_xs[1], Y_ABM - 0.08),
    xytext=(day_xs[4] + 0.40, -0.05),
    fontsize=8.2, color="#222222",
    arrowprops=dict(arrowstyle="->", color="#777777", lw=1.1),
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#fafafa",
              edgecolor="#aaaaaa", linewidth=0.9),
    ha="left", va="center", zorder=7,
)

# ── Save ─────────────────────────────────────────────────────────────────────
out_dir = pathlib.Path(__file__).parent
fig.savefig(out_dir / "oisa_workflow.pdf", dpi=300, bbox_inches="tight")
fig.savefig(out_dir / "oisa_workflow.png", dpi=200, bbox_inches="tight")
print(f"Saved: {out_dir / 'oisa_workflow.pdf'}")
print(f"Saved: {out_dir / 'oisa_workflow.png'}")
