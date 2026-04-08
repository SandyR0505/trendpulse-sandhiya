"""
TrendPulse - Task 3: Analysis with Pandas & NumPy
File: task3_analysis.py

This script loads the cleaned CSV from Task 2,
explores the data, computes statistics using NumPy,
adds new columns, and saves the result for Task 4.
"""

import pandas as pd    # for loading and manipulating data
import numpy as np     # for numerical statistics


# ─────────────────────────────────────────────
# STEP 1 — Load and Explore the Data
# ─────────────────────────────────────────────

# Load the cleaned CSV file created by Task 2
df = pd.read_csv("data/trends_clean.csv")

# Print the shape — how many rows and columns
print(f"Loaded data: {df.shape}")
print()

# Print the first 5 rows to see what the data looks like
print("First 5 rows:")
print(df.head())
print()

# Print average score and average number of comments
avg_score = df["score"].mean()
avg_comments = df["num_comments"].mean()
print(f"Average score   : {avg_score:.3f}")
print(f"Average comments: {avg_comments:.3f}")
print()


# ─────────────────────────────────────────────
# STEP 2 — Basic Analysis with NumPy
# ─────────────────────────────────────────────

print("--- NumPy Stats ---")

# Convert score column to a NumPy array for analysis
scores = np.array(df["score"])

# Mean — average score
mean_score = np.mean(scores)
print(f"Mean score   : {mean_score:.3f}")

# Median — middle value when sorted
median_score = np.median(scores)
print(f"Median score : {median_score:.3f}")

# Standard deviation — how spread out the scores are
std_score = np.std(scores)
print(f"Std deviation: {std_score:.3f}")

# Max and min scores
max_score = np.max(scores)
min_score = np.min(scores)
print(f"Max score    : {max_score}")
print(f"Min score    : {min_score}")
print()

# Which category has the most stories?
# value_counts() counts how many rows each category has
most_common_category = df["category"].value_counts().idxmax()
most_common_count = df["category"].value_counts().max()
print(f"Most stories in: {most_common_category} ({most_common_count} stories)")
print()

# Which story has the most comments?
# idxmax() gives the index (row number) of the maximum value
most_commented_idx = df["num_comments"].idxmax()
most_commented_title = df.loc[most_commented_idx, "title"]
most_commented_count = df.loc[most_commented_idx, "num_comments"]
print(f'Most commented story: "{most_commented_title}" — {most_commented_count} comments')
print()


# ─────────────────────────────────────────────
# STEP 3 — Add New Columns
# ─────────────────────────────────────────────

# engagement = num_comments / (score + 1)
# This tells us how much discussion a story gets per upvote
# We add 1 to score to avoid division by zero
df["engagement"] = df["num_comments"] / (df["score"] + 1)

# is_popular = True if score is above the average score, else False
# This flags stories that are performing better than average
df["is_popular"] = df["score"] > avg_score

# Round engagement to 4 decimal places for cleanliness
df["engagement"] = df["engagement"].round(4)

print("New columns added: 'engagement' and 'is_popular'")
print()


# ─────────────────────────────────────────────
# STEP 4 — Save the Result
# ─────────────────────────────────────────────

# Save the updated DataFrame with the 2 new columns to a new CSV
output_path = "data/trends_analysed.csv"
df.to_csv(output_path, index=False)  # index=False avoids saving row numbers

print(f"Saved to {output_path}")
