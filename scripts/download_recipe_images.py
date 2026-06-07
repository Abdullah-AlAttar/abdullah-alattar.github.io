#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""
Download free recipe images from Pexels and place them as
content/recipes/<slug>/featured.jpg  (recipes)
static/images/tags/<slug>.jpg         (tags)

Usage:
  # Download images for ALL recipes (first-time setup):
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py

  # Download image for a SINGLE new recipe (pass the slug):
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py <slug>

  # Download with a custom search query for a single recipe:
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py <slug> "search query"

  # Download images for ALL tags:
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py --tags

  # Download image for a SINGLE tag:
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py --tags <tag-slug>

  # Force re-download even if an image already exists:
  PEXELS_API_KEY=your_key_here uv run scripts/download_recipe_images.py [--tags] [<slug>] --force

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
TAGS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images", "tags")
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
    "yabraq-mahshi-kusa":    "stuffed zucchini",
}

# ---------------------------------------------------------------------------
# Tag slug (Arabic urlized: spaces → hyphens) → English search query
# Images saved to static/images/tags/<slug>.jpg
# ---------------------------------------------------------------------------
TAGS = {
    "دجاج":           "chicken dish food",
    "لحمة":           "meat dish food",
    "حلويات":        "Arabic sweets dessert",
    "سهل":            "easy quick meal",
    "طبخ-عربي":     "Arabic food spread table",
    "مخبوزات":       "baked goods pastry",
    "معكرونة":        "pasta dish homemade",
    "فرن":            "oven baked tray",
    "صوصات":        "sauce dipping bowl",
    "كيك":            "cake homemade slice",
    "شوكولا":        "chocolate dessert",
    "خضار":          "vegetables colorful",
    "بطاطا":         "potato dish",
    "يخنة":           "stew pot hearty",
    "رز":             "rice pilaf",
    "جبنة":           "cheese melted",
    "نباتي":          "vegetarian healthy meal",
    "مشروبات":       "warm drink cup",
    "ليمون":          "lemon citrus fresh",
    "شوربة":          "soup bowl warm",
    "بزاليا":         "green peas dish",
    "بامية":           "okra stew",
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

def fetch_one_recipe(slug: str, query: str, force: bool) -> bool:
    """Download featured.jpg for a single recipe slug. Returns True on success."""
    dest_dir = os.path.join(RECIPES_DIR, slug)
    dest_file = os.path.join(dest_dir, "featured.jpg")

    if not os.path.isdir(dest_dir):
        print(f"  error  '{slug}' — folder not found: {dest_dir}")
        return False

    if os.path.exists(dest_file) and not force:
        print(f"  skip   {slug}  (already has featured.jpg — use --force to overwrite)")
        return True

    print(f"  fetch  {slug}  ← \"{query}\" ...", end=" ", flush=True)
    try:
        url = search_pexels(query)
        if not url:
            print("no results")
            return False
        download(url, dest_file)
        print("done")
        return True
    except Exception as exc:
        print(f"ERROR: {exc}")
        return False


def fetch_one_tag(slug: str, query: str, force: bool) -> bool:
    """Download <slug>.jpg for a single tag. Returns True on success."""
    os.makedirs(TAGS_DIR, exist_ok=True)
    dest_file = os.path.join(TAGS_DIR, f"{slug}.jpg")

    if os.path.exists(dest_file) and not force:
        print(f"  skip   {slug}  (already has image — use --force to overwrite)")
        return True

    print(f"  fetch  {slug}  ← \"{query}\" ...", end=" ", flush=True)
    try:
        url = search_pexels(query)
        if not url:
            print("no results")
            return False
        download(url, dest_file)
        print("done")
        return True
    except Exception as exc:
        print(f"ERROR: {exc}")
        return False


def _bulk(items: dict, fetch_fn, dest_fn, force: bool) -> None:
    ok = skip = fail = 0
    for slug, query in items.items():
        result = fetch_fn(slug, query, force)
        dest = dest_fn(slug)
        if result:
            if not force and os.path.exists(dest):
                skip += 1
            else:
                ok += 1
        else:
            fail += 1
        time.sleep(DELAY)
    print(f"\nFinished: {ok} downloaded, {skip} skipped, {fail} failed")


def main():
    if not API_KEY:
        print("Error: set the PEXELS_API_KEY environment variable.")
        print("  Get a free key at https://www.pexels.com/api/")
        sys.exit(1)

    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    tag_mode = "--tags" in args
    args = [a for a in args if a != "--tags"]

    # ---- Tag mode ----------------------------------------------------------
    if tag_mode:
        if args:
            # Single tag
            slug = args[0]
            query = args[1] if len(args) >= 2 else TAGS.get(slug)
            if not query:
                print(f"Warning: '{slug}' is not in the TAGS map.")
                print(f"  Pass a query: uv run scripts/download_recipe_images.py --tags {slug} \"search query\"")
                sys.exit(1)
            success = fetch_one_tag(slug, query, force)
            if slug not in TAGS:
                print(f"\nReminder: add this entry to the TAGS dict in the script:")
                print(f'    "{slug}": "{query}",')
            sys.exit(0 if success else 1)
        else:
            # All tags
            print("Downloading tag images...")
            _bulk(
                TAGS,
                fetch_one_tag,
                lambda slug: os.path.join(TAGS_DIR, f"{slug}.jpg"),
                force,
            )
            return

    # ---- Recipe single mode ------------------------------------------------
    if args:
        slug = args[0]
        if slug not in RECIPES and len(args) < 2:
            print(f"Warning: '{slug}' is not in the RECIPES map.")
            print("  Either add it to RECIPES in the script, or pass a query as the second argument.")
            print(f"  Example: uv run scripts/download_recipe_images.py {slug} \"my search query\"")
            sys.exit(1)

        query = args[1] if len(args) >= 2 else RECIPES[slug]
        success = fetch_one_recipe(slug, query, force)

        if slug not in RECIPES:
            print(f"\nReminder: add this entry to the RECIPES dict in the script:")
            print(f'    "{slug}": "{query}",')

        sys.exit(0 if success else 1)

    # ---- Bulk recipes mode -------------------------------------------------
    print("Downloading recipe images...")
    _bulk(
        RECIPES,
        fetch_one_recipe,
        lambda slug: os.path.join(RECIPES_DIR, slug, "featured.jpg"),
        force,
    )


if __name__ == "__main__":
    main()
