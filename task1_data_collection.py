

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "https://hacker-news.firebaseio.com/v0"
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# Fetch from 3 endpoints to get more variety
STORY_ENDPOINTS = ["topstories", "beststories", "newstories"]
IDS_PER_ENDPOINT = 200
MAX_PER_CATEGORY = 25

CATEGORIES = {
    "technology": [
        "AI", "software", "tech", "code", "computer", "data", "cloud",
        "API", "GPU", "LLM", "open source", "developer", "programming",
        "startup", "model", "robot", "chip", "hardware", "security",
        "hack", "python", "linux", "web", "app", "tool", "database",
        "framework", "algorithm", "machine learning", "neural", "server",
        "network", "cyber", "encryption", "bug", "github", "microsoft",
        "google", "apple", "amazon", "meta"
    ],
    "worldnews": [
        "war", "government", "country", "president", "election",
        "climate", "attack", "global", "policy", "law", "court",
        "military", "china", "russia", "europe", "ukraine", "india",
        "iran", "sanctions", "nuclear", "treaty", "crisis", "senate",
        "congress", "parliament", "minister", "diplomat", "border",
        "tariff", "trade", "economy", "inflation", "recession", "tax",
        "protest", "rights", "immigration", "refugee", "conflict"
    ],
    "sports": [
        "NFL", "NBA", "FIFA", "sport", "team", "player", "league",
        "championship", "tennis", "soccer", "football", "baseball",
        "olympic", "tournament", "match", "coach", "win", "loss",
        "score", "athlete", "stadium", "season", "draft", "transfer",
        "cricket", "rugby", "golf", "swimming", "race", "marathon",
        "trophy", "medal", "world cup", "playoffs", "finals"
    ],
    "science": [
        "research", "study", "space", "physics", "biology", "discovery",
        "NASA", "genome", "ocean", "planet", "quantum", "medicine",
        "vaccine", "cancer", "brain", "evolution", "asteroid",
        "telescope", "gene", "experiment", "laboratory", "scientist",
        "journal", "published", "fossil", "species", "molecule",
        "protein", "DNA", "RNA", "surgery", "health", "nutrition",
        "psychology", "neuroscience", "chemistry"
    ],
    "entertainment": [
        "movie", "film", "music", "Netflix", "book", "show", "award",
        "streaming", "spotify", "youtube", "disney", "hbo", "album",
        "concert", "actor", "director", "series", "episode", "trailer",
        "review", "bestseller", "novel", "podcast", "video", "game",
        "gaming", "playstation", "xbox", "nintendo", "anime", "comic",
        "art", "exhibition", "festival", "theatre", "dance"
    ],
}


def assign_category(title):
    """Check title against keywords and return matching category."""
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return category
    return None


def fetch_all_story_ids():
    """Fetch story IDs from 3 endpoints and combine (no duplicates)."""
    all_ids = []
    seen = set()

    for endpoint in STORY_ENDPOINTS:
        url = f"{BASE_URL}/{endpoint}.json"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            ids = response.json()[:IDS_PER_ENDPOINT]
            for story_id in ids:
                if story_id not in seen:
                    all_ids.append(story_id)
                    seen.add(story_id)
            print(f"  Fetched IDs from {endpoint}")
        except requests.RequestException as e:
            print(f"[WARNING] Could not fetch {endpoint}: {e}")

    print(f"Total unique story IDs: {len(all_ids)}\n")
    return all_ids


def fetch_story(story_id):
    """Fetch a single story by ID. Returns None if it fails."""
    url = f"{BASE_URL}/item/{story_id}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[WARNING] Failed to fetch story {story_id}: {e}")
        return None


def extract_fields(story, category):
    """Extract the 7 required fields from a story."""
    return {
        "post_id":      story.get("id"),
        "title":        story.get("title", ""),
        "category":     category,
        "score":        story.get("score", 0),
        "num_comments": story.get("descendants", 0),
        "author":       story.get("by", ""),
        "collected_at": datetime.now().isoformat(),
    }


def main():
    # Step 1: Get story IDs from 3 endpoints
    print("Fetching story IDs from HackerNews (3 endpoints)...")
    story_ids = fetch_all_story_ids()

    if not story_ids:
        print("No story IDs retrieved. Exiting.")
        return

    # Step 2: Fetch all story details
    print("Fetching individual story details (this may take a moment)...")
    all_stories = []
    for story_id in story_ids:
        story = fetch_story(story_id)
        if story and story.get("title") and story.get("type") == "story":
            all_stories.append(story)

    print(f"Fetched details for {len(all_stories)} valid stories.\n")

    # Step 3: Categorise and collect up to 25 per category
    collected = []
    category_counts = {cat: 0 for cat in CATEGORIES}

    for category in CATEGORIES:
        print(f"Processing category: {category}")

        for story in all_stories:
            if category_counts[category] >= MAX_PER_CATEGORY:
                break
            title = story.get("title", "")
            if assign_category(title) == category:
                collected.append(extract_fields(story, category))
                category_counts[category] += 1

        print(f"  -> Collected {category_counts[category]} stories")
        time.sleep(2)  # wait 2 seconds between categories

    # Step 4: Save to data/trends_YYYYMMDD.json
    os.makedirs("data", exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")
    output_path = f"data/trends_{today_str}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)

    print(f"\nCollected {len(collected)} stories. Saved to {output_path}")


if __name__ == "__main__":
    main()
