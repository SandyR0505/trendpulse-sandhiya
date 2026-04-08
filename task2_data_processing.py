"""
TrendPulse - Task 2: Clean the Data & Save as CSV
File: task2_data_processing.py """

import pandas as pd   # for loading, cleaning, and saving data
import os             # for creating folders
import glob           # for finding files by pattern


# ─────────────────────────────────────────────
# STEP 1 — Load the JSON file into a DataFrame
# ─────────────────────────────────────────────

# Find the JSON file in the data/ folder (name changes by date)
# glob finds all files matching the pattern data/trends_*.json
json_files = glob.glob("data/trends_*.json")

# Make sure we found at least one file
if not json_files:
    print("ERROR: No JSON file found in data/ folder.")
    print("Please run task1_data_collection.py first!")
    exit()


json_file = sorted(json_files)[-1]

# Load the JSON file into a Pandas DataFrame
df = pd.read_json(json_file)

# Print how many rows were loaded
print(f"Loaded {len(df)} stories from {json_file}")
print()


# ─────────────────────────────────────────────
# STEP 2 — Clean the Data
# ─────────────────────────────────────────────

# --- 2a: Remove duplicate rows by post_id ---
# Same story might appear twice — keep only first occurrence
df = df.drop_duplicates(subset="post_id")
print(f"After removing duplicates: {len(df)}")

# --- 2b: Drop rows where important fields are missing ---
# We need post_id, title, and score to be present
df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

# --- 2c: Fix data types ---
# score and num_comments must be integers, not floats
df["score"] = df["score"].astype(int)
df["num_comments"] = df["num_comments"].fillna(0).astype(int)
df["post_id"] = df["post_id"].astype(int)

# --- 2d: Remove low quality stories (score < 5) ---
# Low score means the story is not popular or relevant
df = df[df["score"] >= 5]
print(f"After removing low scores: {len(df)}")

# --- 2e: Strip extra whitespace from title ---
# Remove any leading/trailing spaces from story titles
df["title"] = df["title"].str.strip()

print()


# ─────────────────────────────────────────────
# STEP 3 — Save as CSV
# ─────────────────────────────────────────────

# Make sure the data/ folder exists
os.makedirs("data", exist_ok=True)

# Save cleaned DataFrame to CSV (index=False avoids saving row numbers)
output_path = "data/trends_clean.csv"
df.to_csv(output_path, index=False)

# Print confirmation message
print(f"Saved {len(df)} rows to {output_path}")
print()

# Print stories per category summary
print("Stories per category:")
category_counts = df["category"].value_counts()
for category, count in category_counts.items():
    print(f"  {category:<20} {count}")
