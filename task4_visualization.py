"""
TrendPulse - Task 4: Visualizations
File: task4_visualization.py

This script loads the analysed CSV from Task 3 and creates
3 charts plus a combined dashboard using Matplotlib.
All charts are saved as PNG files in the outputs/ folder.
"""

import pandas as pd          # for loading the CSV
import matplotlib.pyplot as plt  # for creating charts
import matplotlib.colors as mcolors  # for custom colours
import os                    # for creating the outputs/ folder
import numpy as np           # for any numerical operations


# ─────────────────────────────────────────────
# STEP 1 — Setup
# ─────────────────────────────────────────────

# Load the analysed CSV file created by Task 3
df = pd.read_csv("data/trends_analysed.csv")
print(f"Loaded {len(df)} rows from data/trends_analysed.csv")

# Create the outputs/ folder if it doesn't exist
os.makedirs("outputs", exist_ok=True)
print("outputs/ folder ready")
print()

# Convert is_popular column to boolean (it may be stored as string)
df["is_popular"] = df["is_popular"].astype(str).str.upper() == "TRUE"


# ─────────────────────────────────────────────
# CHART 1 — Top 10 Stories by Score
# ─────────────────────────────────────────────

# Sort by score descending and take the top 10
top10 = df.sort_values("score", ascending=False).head(10)

# Shorten titles longer than 50 characters for readability
top10 = top10.copy()
top10["short_title"] = top10["title"].apply(
    lambda t: t[:47] + "..." if len(t) > 50 else t
)

# Create a horizontal bar chart
fig1, ax1 = plt.subplots(figsize=(12, 6))

# Plot bars horizontally — y axis = titles, x axis = scores
bars = ax1.barh(
    top10["short_title"],
    top10["score"],
    color="steelblue",
    edgecolor="white"
)

# Add score value labels at the end of each bar
for bar in bars:
    width = bar.get_width()
    ax1.text(
        width + 5, bar.get_y() + bar.get_height() / 2,
        str(int(width)),
        va="center", fontsize=9
    )

# Invert y-axis so highest score is at the top
ax1.invert_yaxis()

# Add title and axis labels
ax1.set_title("Top 10 Stories by Score", fontsize=14, fontweight="bold", pad=15)
ax1.set_xlabel("Score (Upvotes)", fontsize=11)
ax1.set_ylabel("Story Title", fontsize=11)

# Adjust layout so titles don't get cut off
plt.tight_layout()

# Save BEFORE show (required)
plt.savefig("outputs/chart1_top_stories.png", dpi=150, bbox_inches="tight")
print("Saved: outputs/chart1_top_stories.png")
plt.close()  # close to free memory


# ─────────────────────────────────────────────
# CHART 2 — Stories per Category
# ─────────────────────────────────────────────

# Count how many stories are in each category
category_counts = df["category"].value_counts()

# Use a different colour for each bar
colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

fig2, ax2 = plt.subplots(figsize=(9, 5))

# Plot vertical bar chart
bars2 = ax2.bar(
    category_counts.index,
    category_counts.values,
    color=colors[:len(category_counts)],
    edgecolor="white",
    width=0.6
)

# Add count labels on top of each bar
for bar in bars2:
    height = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2, height + 0.3,
        str(int(height)),
        ha="center", va="bottom", fontsize=10, fontweight="bold"
    )

# Add title and axis labels
ax2.set_title("Number of Stories per Category", fontsize=14, fontweight="bold", pad=15)
ax2.set_xlabel("Category", fontsize=11)
ax2.set_ylabel("Number of Stories", fontsize=11)
ax2.set_ylim(0, category_counts.max() + 5)  # a bit of space above bars

plt.tight_layout()
plt.savefig("outputs/chart2_categories.png", dpi=150, bbox_inches="tight")
print("Saved: outputs/chart2_categories.png")
plt.close()


# ─────────────────────────────────────────────
# CHART 3 — Score vs Comments (Scatter Plot)
# ─────────────────────────────────────────────

# Separate popular and non-popular stories using is_popular column
popular = df[df["is_popular"] == True]
not_popular = df[df["is_popular"] == False]

fig3, ax3 = plt.subplots(figsize=(9, 6))

# Plot non-popular stories in blue
ax3.scatter(
    not_popular["score"],
    not_popular["num_comments"],
    color="steelblue",
    alpha=0.6,           # slight transparency so dots don't overlap badly
    label="Not Popular",
    edgecolors="white",
    s=60                 # dot size
)

# Plot popular stories in orange
ax3.scatter(
    popular["score"],
    popular["num_comments"],
    color="darkorange",
    alpha=0.8,
    label="Popular (above avg score)",
    edgecolors="white",
    s=80
)

# Add title, axis labels, and legend
ax3.set_title("Score vs Number of Comments", fontsize=14, fontweight="bold", pad=15)
ax3.set_xlabel("Score (Upvotes)", fontsize=11)
ax3.set_ylabel("Number of Comments", fontsize=11)
ax3.legend(fontsize=10)

plt.tight_layout()
plt.savefig("outputs/chart3_scatter.png", dpi=150, bbox_inches="tight")
print("Saved: outputs/chart3_scatter.png")
plt.close()


# ─────────────────────────────────────────────
# BONUS — Combined Dashboard
# ─────────────────────────────────────────────

# Create a figure with 1 row and 3 columns of subplots
fig, (ax_a, ax_b, ax_c) = plt.subplots(1, 3, figsize=(20, 6))

# Add overall dashboard title
fig.suptitle("TrendPulse Dashboard", fontsize=18, fontweight="bold", y=1.02)

# -- Dashboard Panel 1: Top 10 Stories --
top10_d = df.sort_values("score", ascending=False).head(10).copy()
top10_d["short_title"] = top10_d["title"].apply(
    lambda t: t[:30] + "..." if len(t) > 30 else t
)
ax_a.barh(top10_d["short_title"], top10_d["score"], color="steelblue")
ax_a.invert_yaxis()
ax_a.set_title("Top 10 Stories by Score", fontsize=10, fontweight="bold")
ax_a.set_xlabel("Score")
ax_a.tick_params(axis="y", labelsize=7)

# -- Dashboard Panel 2: Stories per Category --
ax_b.bar(
    category_counts.index,
    category_counts.values,
    color=colors[:len(category_counts)]
)
ax_b.set_title("Stories per Category", fontsize=10, fontweight="bold")
ax_b.set_xlabel("Category")
ax_b.set_ylabel("Count")
ax_b.tick_params(axis="x", rotation=15)

# -- Dashboard Panel 3: Score vs Comments --
ax_c.scatter(
    not_popular["score"], not_popular["num_comments"],
    color="steelblue", alpha=0.6, label="Not Popular", s=40
)
ax_c.scatter(
    popular["score"], popular["num_comments"],
    color="darkorange", alpha=0.8, label="Popular", s=50
)
ax_c.set_title("Score vs Comments", fontsize=10, fontweight="bold")
ax_c.set_xlabel("Score")
ax_c.set_ylabel("Comments")
ax_c.legend(fontsize=8)

plt.tight_layout()
plt.savefig("outputs/dashboard.png", dpi=150, bbox_inches="tight")
print("Saved: outputs/dashboard.png")
plt.close()

print()
print("All charts saved to outputs/ folder!")
