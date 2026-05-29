---
description: "Add a new recipe to Mom's Recipes Hugo site. Use when the user provides recipe text in Arabic (ingredients, steps) and wants it added as a new page bundle under content/recipes/."
agent: "agent"
tools: ["create_file", "read_file", "run_in_terminal"]
---

# Add Recipe

You are adding a new recipe to an Arabic-first Hugo recipe site (Mom's Recipes / وصفات ماما).

## Recipe Format

Each recipe is a Hugo Page Bundle at `content/recipes/<slug>/index.ar.md`.

The slug should be a transliterated short name of the dish (e.g., `jaj-mahbal`, `bameh-blahmeh`, `bazalia-bmara2a`).

## Template

```yaml
---
title: "<recipe name in Arabic>"
date: <YYYY-MM-DD of today>
tags: [<relevant Arabic tags — food type, main ingredient, cooking style>]
ingredients:
  - "<ingredient 1>"
  - "<ingredient 2>"
---

## طريقة التحضير

1. <step 1>
2. <step 2>
```

## Rules

1. **Extract ingredients** from the recipe text into a clean YAML list in front matter.
2. **Format steps** as a numbered Markdown list — one logical step per item. Clean up the text slightly for readability but preserve the colloquial Arabic voice and dialect exactly as given.
3. **Tags**: Pick 3-5 relevant tags in Arabic. Reuse existing tags when possible: دجاج، لحمة، بامية، بزاليا، بطاطا، يخنة، شوربة، طبخ عربي، صحي، سهل، خضار، ليمون
4. **Slug**: Use a romanized/transliterated short name. No spaces, use hyphens.
5. **Date**: Use today's date.
6. **Image**: If the user provides an image, save it as `featured.jpg` in the same folder. Otherwise skip it.
7. **Notes/tips** from the user that aren't steps should go as a blockquote (`> **ملاحظة:**`) at the end.
8. **Do NOT** translate or formalize the Arabic. Keep the original dialect (شامي/levantine).

## After Creating

Run `hugo --minify` to verify the recipe builds without errors. Report the recipe title and path to the user.
