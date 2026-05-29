# وصفات ماما — Mom's Recipes

موقع وصفات ثابت (static) مبني بـ Hugo مع بحث كامل النص بالعربي عبر Pagefind.

## المتطلبات

- [Hugo Extended](https://gohugo.io/installation/) (v0.158+)
- [Node.js](https://nodejs.org/) (for Pagefind)
- [Task](https://taskfile.dev/) (go-task, optional — for convenience commands)

## التشغيل المحلي

```bash
# تشغيل سيرفر التطوير (بدون بحث)
task dev

# بناء كامل مع فهرسة البحث
task build

# بناء + تشغيل سيرفر محلي مع البحث شغّال
task serve
```

## إضافة وصفة جديدة

### 1. أنشئ مجلد الوصفة

```bash
task new -- اسم-الوصفة
```

أو يدوياً:

```
content/recipes/اسم-الوصفة/
├── index.ar.md      # محتوى الوصفة
└── featured.jpg     # صورة الوصفة (اختياري)
```

### 2. اكتب محتوى الوصفة

```yaml
---
title: "اسم الوصفة"
date: 2025-01-15
image: featured.jpg
tags: ["تصنيف١", "تصنيف٢", "تصنيف٣"]
ingredients:
  - "مكوّن ١"
  - "مكوّن ٢"
  - "مكوّن ٣"
---

## طريقة التحضير

1. الخطوة الأولى...
2. الخطوة الثانية...
3. الخطوة الثالثة...
```

### 3. أضف صورة (اختياري)

ضع صورة باسم `featured.jpg` (أو `.png`/`.webp`) في نفس مجلد الوصفة.
Hugo يقوم تلقائياً بتصغيرها وتحويلها لـ WebP.

### 4. انشر

```bash
git add .
git commit -m "وصفة جديدة: اسم الوصفة"
git push
```

GitHub Actions يبني الموقع ويفهرس البحث وينشر تلقائياً خلال 2-3 دقائق.

## هيكل المشروع

```
├── hugo.toml                  # إعدادات Hugo
├── i18n/
│   ├── ar.yaml                # نصوص الواجهة بالعربي
│   └── en.yaml                # نصوص الواجهة بالإنجليزي
├── content/recipes/           # الوصفات (مجلد لكل وصفة)
├── layouts/                   # القوالب
├── assets/scss/               # الأنماط (SCSS)
├── .github/workflows/         # CI/CD pipeline
└── Taskfile.yml               # أوامر مختصرة
```

## البحث

البحث يعمل عبر [Pagefind](https://pagefind.app/) — يُفهرس كل كلمة في كل وصفة وقت البناء:
- اسم الوصفة
- المكونات
- خطوات التحضير
- التصنيفات

البحث يعمل بالكامل في المتصفح بدون سيرفر.

> **ملاحظة:** البحث لا يعمل مع `task dev` (hugo server) لأن Pagefind يحتاج بناء كامل أولاً.
> استخدم `task serve` لتجربة البحث محلياً.

## النشر

الموقع ينشر تلقائياً على GitHub Pages عند كل push لـ branch الـ `master`.

