#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""
Download free recipe images from Pexels and place them as
content/recipes/<slug>/featured.jpg

Usage:
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py

Get a free API key at: https://www.pexels.com/api/
"""

import os
import sys
import time
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("PEXELS_API_KEY", "")
RECIPES_DIR = os.path.join(os.path.dirname(__file__), "..", "content", "recipes")
PEXELS_SEARCH = "https://api.pexels.com/v1/search"
IMAGE_SIZE = "large"   # large = ~1280px wide, good for Hugo processing
DELAY = 0.5            # seconds between requests (be polite to the API)

# ---------------------------------------------------------------------------
# Recipe slug → English search query mapping
# ---------------------------------------------------------------------------
RECIPES = {
    "ajja":                  "egg omelette Arabic",
    "bameh-blahmeh":         "okra meat stew",
    "basbousa-qashta":       "basbousa cream semolina cake",
    "basbousa-sada":         "semolina cake Middle Eastern",
    "bazalia-bmara2a":       "peas meat stew",
    "burghul-banadora":      "bulgur tomato pilaf",
    "fattet-jaj":            "chicken fatteh Arabic dish",
    "fettuccini-jaj":        "chicken fettuccine cream pasta",
    "hala-mars":             "chocolate Mars bar dessert",
    "jaj-furn":              "oven baked chicken",
    "jaj-mahbal":            "roasted whole chicken",
    "jaj-masluq":            "boiled chicken broth",
    "kabsa-jaj":             "kabsa chicken rice Saudi",
    "kabsa-lahmeh":          "kabsa lamb rice Saudi",
    "kastarad-fawakeh":      "custard fruit dessert",
    "kek-burtuqal":          "orange cake homemade",
    "kek-shamwah":           "chiffon sponge cake",
    "kek-shokolah":          "chocolate cake homemade",
    "kek-vanilla":           "vanilla cake homemade",
    "kuwaj":                 "meat vegetable casserole bake",
    "lahmeh-siniyeh":        "minced meat bake tray",
    "lazanya":               "lasagna homemade",
    "makarona-jubna":        "pasta cheese baked",
    "makarona-salsa":        "pasta tomato sauce",
    "manzaleh":              "eggplant meat casserole",
    "milfeh":                "mille feuille pastry cream",
    "mujaddara":             "mujaddara lentils rice",
    "sahlab":                "sahlab hot milk drink",
    "shawarma-jaj":          "chicken shawarma wrap",
    "shorbet-adas":          "lentil soup bowl",
    "sous-banadora-basit":   "fresh tomato sauce",
    "sous-banadora-makarona":"pasta tomato sauce pan",
    "sous-mozzarella":       "mozzarella cheese sauce",
    "sous-toum":             "garlic toum sauce white",
    "tart-mabrosha":         "jam tart pastry dessert",
    "tasali-biskot-shokolah":"chocolate biscuit no bake dessert",
    "tasali-nescafe":        "nescafe coffee biscuit dessert",
    "tatbilt-jaj":           "chicken spice marinade",
    "waraq-inab-kousa":      "stuffed grape leaves zucchini",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def search_pexels(query: str) -> str | None:
    """Return the URL of the first Pexels photo for the given query."""
    resp = requests.get(
        PEXELS_SEARCH,
        headers={"Authorization": API_KEY},
        params={"query": query, "per_page": 1, "orientation": "landscape"},
        timeout=15,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        return None
    return photos[0]["src"][IMAGE_SIZE]


def download(url: str, dest: str) -> None:
    resp = requests.get(url, timeout=30, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            fh.write(chunk)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not API_KEY:
        print("Error: set the PEXELS_API_KEY environment variable.")
        print("  Get a free key at https://www.pexels.com/api/")
        sys.exit(1)

    ok = skip = fail = 0

    for slug, query in RECIPES.items():
        dest_dir = os.path.join(RECIPES_DIR, slug)
        dest_file = os.path.join(dest_dir, "featured.jpg")

        if os.path.exists(dest_file):
            print(f"  skip  {slug}  (already has featured.jpg)")
            skip += 1
            continue

        if not os.path.isdir(dest_dir):
            print(f"  warn  {slug}  (folder not found, skipping)")
            fail += 1
            continue

        print(f"  fetch {slug}  ← \"{query}\" ...", end=" ", flush=True)
        try:
            url = search_pexels(query)
            if not url:
                print("no results")
                fail += 1
                continue
            download(url, dest_file)
            print("done")
            ok += 1
        except Exception as exc:
            print(f"ERROR: {exc}")
            fail += 1

        time.sleep(DELAY)

    print(f"\nFinished: {ok} downloaded, {skip} skipped, {fail} failed")


if __name__ == "__main__":
    main()
