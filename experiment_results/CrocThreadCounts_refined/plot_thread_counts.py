"""Heatmap of crocsort running time by (genThreads, mergeThreads).

Averages all repetitions for each thread-count pair from
crocThreadCountTests.csv and writes crocThreadCountTests.png next to it.
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

here = Path(__file__).resolve().parent
csv_path = here / "crocThreadCountTests.csv"
out_path = here / "crocThreadCountTests.png"

times = defaultdict(list)
with open(csv_path, newline="") as f:
    for row in csv.DictReader(f):
        key = (int(row["genThreads"]), int(row["mergeThreads"]))
        times[key].append(float(row["runningTime (ms)"]) / 1000)  # seconds

gen_counts = sorted({g for g, _ in times})
merge_counts = sorted({m for _, m in times})

grid = np.full((len(gen_counts), len(merge_counts)), np.nan)
for i, g in enumerate(gen_counts):
    for j, m in enumerate(merge_counts):
        if (g, m) in times:
            grid[i, j] = np.mean(times[(g, m)])

fig, ax = plt.subplots(figsize=(7, 6))
# Gradient spans the fastest to the slowest averaged cell.
cmap = LinearSegmentedColormap.from_list(
    "green_to_red", ["green", "yellow", "orange", "red"])
im = ax.imshow(grid, cmap=cmap,
               vmin=np.nanmin(grid), vmax=np.nanmax(grid), origin="lower")

ax.set_xticks(range(len(merge_counts)), labels=merge_counts)
ax.set_yticks(range(len(gen_counts)), labels=gen_counts)
ax.set_xlabel("Merge threads")
ax.set_ylabel("Run-gen threads")
ax.set_title("crocsort mean running time (s)")

# Grid lines between cells.
ax.set_xticks(np.arange(-0.5, len(merge_counts)), minor=True)
ax.set_yticks(np.arange(-0.5, len(gen_counts)), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="minor", length=0)

# Annotate each cell with its mean time.
for i in range(len(gen_counts)):
    for j in range(len(merge_counts)):
        v = grid[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", color="black")

fig.colorbar(im, ax=ax, label="Mean running time (s)")
fig.tight_layout()
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
plt.show()
