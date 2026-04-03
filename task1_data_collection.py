

import requests   # for making HTTP requests
import json       # for saving data as JSON
import time       # for sleep between category loops
import os         # for creating the data/ folder
from datetime import datetime  # for the collected_at timestamp

BASE_URL = "https://hacker-news.firebaseio.com/v0"

HEADERS = {"User-Agent": "TrendPulse/1.0"}

# Number of top story IDs to pull from HackerNews
TOP_N = 500
MAX_PER_CATEGORY = 25

# Category → keyword mapping (case-insensitive matching)
CATEGORIES = {
    "technology":    ["AI", "software", "tech", "code", "computer",
                      "data", "cloud", "API", "GPU", "LLM", "open source",
                      "developer", "programming", "startup", "model",
                      "robot", "chip", "hardware", "security", "hack",
                      "python", "linux", "web", "app", "tool"],
    "worldnews":     ["war", "government", "country", "president",
                      "election", "climate", "attack", "global",
                      "policy", "law", "court", "military", "china",
                      "russia", "europe", "ukraine", "india", "iran",
                      "sanctions", "nuclear", "treaty", "crisis"],
    "sports":        ["NFL", "NBA", "FIFA", "sport", "game", "team",
                      "player", "league", "championship", "tennis",
                      "soccer", "football", "baseball", "olympic",
                      "tournament", "match", "coach", "win", "loss"],
    "science":       ["research", "study", "space", "physics",
                      "biology", "discovery", "NASA", "genome",
                      "climate", "ocean", "planet", "quantum",
                      "medicine", "vaccine", "cancer", "brain",
                      "evolution", "asteroid", "telescope", "gene"],
    "entertainment": ["movie", "film", "music", "Netflix", "game",
                      "book", "show", "award", "streaming", "spotify",
                      "youtube", "disney", "apple tv", "hbo",
                      "album", "concert", "actor", "director", "series"],
}


def assign_category(title):
    """
    Check the story title against each category's keyword list.
    Returns the first matching category name, or None if no match.
    Matching is case-insensitive.
    """
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return category   # stop at the first match
    return None  # story doesn't fit any category


# ─────────────────────────────────────────────
# STEP 1: Fetch the top 500 story IDs
# ─────────────────────────────────────────────

def fetch_top_story_ids():
    """
    Calls the /topstories endpoint and returns the first TOP_N IDs.
    Returns an empty list if the request fails.
    """
    url = f"{BASE_URL}/topstories.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()          # raises for 4xx/5xx errors
        all_ids = response.json()            # full list (up to ~500)
        return all_ids[:TOP_N]              # keep only what we need
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch top story IDs: {e}")
        return []


# ─────────────────────────────────────────────
# STEP 2: Fetch details for a single story ID
# ─────────────────────────────────────────────

def fetch_story(story_id):
    """
    Fetches one story's JSON object by ID.
    Returns the story dict, or None if the request fails.
    """
    url = f"{BASE_URL}/item/{story_id}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Don't crash – just log and continue
        print(f"[WARNING] Failed to fetch story {story_id}: {e}")
        return None


# ─────────────────────────────────────────────
# STEP 3: Extract the 7 required fields
# ─────────────────────────────────────────────

def extract_fields(story, category):
    """
    Pulls out exactly the 7 fields we need from a raw HackerNews story dict.
    'collected_at' is added by us (current timestamp).
    """
    return {
        "post_id":      story.get("id"),            # unique story ID
        "title":        story.get("title", ""),     # story headline
        "category":     category,                   # our assigned category
        "score":        story.get("score", 0),      # upvote count
        "num_comments": story.get("descendants", 0),# comment count
        "author":       story.get("by", ""),        # poster username
        "collected_at": datetime.now().isoformat(), # when we pulled this
    }


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def main():
    # -- Get the top story IDs first --
    print("Fetching top story IDs from HackerNews...")
    story_ids = fetch_top_story_ids()
    if not story_ids:
        print("No story IDs retrieved. Exiting.")
        return

    print(f"Retrieved {len(story_ids)} story IDs. Starting categorisation...\n")

    # -- Pre-fetch all story details once, so we can reuse them per category --
    # This avoids hitting the API once per category for the same stories.
    print("Fetching individual story details (this may take a moment)...")
    all_stories = []
    for story_id in story_ids:
        story = fetch_story(story_id)
        if story and story.get("title"):   # skip items with no title (jobs, etc.)
            all_stories.append(story)

    print(f"Fetched details for {len(all_stories)} valid stories.\n")

    # -- Categorise stories and collect up to 25 per category --
    collected = []                         # final list of formatted story dicts
    category_counts = {cat: 0 for cat in CATEGORIES}  # track per-category totals

    for category in CATEGORIES:
        print(f"Processing category: {category}")

        for story in all_stories:
            # Stop once we have 25 stories for this category
            if category_counts[category] >= MAX_PER_CATEGORY:
                break

            title = story.get("title", "")
            assigned = assign_category(title)

            if assigned == category:
                # Extract the 7 required fields and add to our collection
                record = extract_fields(story, category)
                collected.append(record)
                category_counts[category] += 1

        print(f"  → Collected {category_counts[category]} stories")

        time.sleep(2)

    os.makedirs("data", exist_ok=True)   

    today_str = datetime.now().strftime("%Y%m%d")
    output_path = f"data/trends_{today_str}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)

    
    print(f"\nCollected {len(collected)} stories. Saved to {output_path}")



if __name__ == "__main__":
    main()
