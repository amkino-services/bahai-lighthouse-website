#!/usr/bin/env bash
set -euo pipefail

DEPLOY_DIR=".deploy"

echo "===== BAHÁ'Í LIGHTHOUSE — BUILD DEPLOYMENT ====="

rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

copy_file() {
  local source="$1"
  local destination="$2"

  if [[ ! -f "$source" ]]; then
    echo "❌ Missing source file: $source"
    exit 1
  fi

  mkdir -p "$DEPLOY_DIR/$(dirname "$destination")"
  cp "$source" "$DEPLOY_DIR/$destination"
  echo "COPY  $source -> $destination"
}

echo
echo "===== MAIN PAGES ====="

for file in pages/main/*.html; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== CALENDAR PAGES ====="

for file in pages/calendar/*.html; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== TOOL PAGES ====="

for file in pages/tools/*.html; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== NEWSLETTER PAGES ====="

for file in pages/newsletter/*.html; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== COMMUNITY LANDING PAGE ====="

copy_file \
  "pages/community/community.html" \
  "community.html"

echo
echo "===== COMMUNITY EXPERIENCE PAGES ====="

for file in pages/community/experiences/*.html; do
  copy_file "$file" "community/$(basename "$file")"
done

echo
echo "===== COMMUNITY PATH PAGES ====="

for file in pages/community/paths/*.html; do
  copy_file "$file" "community/paths/$(basename "$file")"
done

echo
echo "===== STYLES ====="

copy_file "styles/styles.css" "styles.css"
copy_file "styles/community-path.css" "community-path.css"

echo
echo "===== SHARED JAVASCRIPT ====="

for file in scripts/shared/*.js; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== CALENDAR JAVASCRIPT ====="

for file in scripts/calendar/*.js; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== TOOL JAVASCRIPT ====="

for file in scripts/tools/*.js; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== COMMUNITY JAVASCRIPT ====="

for file in scripts/community/*.js; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== NEWSLETTER JAVASCRIPT ====="

for file in scripts/newsletter/*.js; do
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== PUBLIC ROOT FILES ====="

for file in public/*; do
  [[ -f "$file" ]] || continue
  copy_file "$file" "$(basename "$file")"
done

echo
echo "===== ASSETS ====="

if [[ -d assets ]]; then
  mkdir -p "$DEPLOY_DIR/assets"
  while IFS= read -r -d '' file; do
    relative="${file#assets/}"
    mkdir -p "$DEPLOY_DIR/assets/$(dirname "$relative")"
    cp "$file" "$DEPLOY_DIR/assets/$relative"
  done < <(find assets -type f ! -name '.DS_Store' -print0)
  echo "COPY  assets/ -> assets/"
fi

echo
echo "===== PUBLIC DATA ====="

if [[ -d data/community ]]; then
  mkdir -p "$DEPLOY_DIR/data/community"
  while IFS= read -r -d '' file; do
    relative="${file#data/community/}"
    mkdir -p "$DEPLOY_DIR/data/community/$(dirname "$relative")"
    cp "$file" "$DEPLOY_DIR/data/community/$relative"
  done < <(find data/community -type f ! -name '.DS_Store' -print0)
  echo "COPY  data/community/ -> data/community/"
fi

echo
echo "===== SECURITY SCAN ====="

if find "$DEPLOY_DIR" -type f | grep -Ei \
'(^|/)(\.env|\.gitignore|\.DS_Store|wrangler.*|package(-lock)?\.json|README\.md|.*backup.*|.*before-.*|.*\.bak|.*\.old|.*\.key|.*\.pem|.*secret.*|.*credential.*)$'
then
  echo
  echo "❌ SECURITY CHECK FAILED"
  echo "Deployment directory contains a forbidden file."
  exit 1
fi

echo "✅ No forbidden deployment files found."

echo
echo "===== REQUIRED FILE CHECK ====="

required_files=(
  "index.html"
  "styles.css"
  "site-header.js"
  "site-footer.js"
  "community.html"
  "community/paths/childrens-classes.html"
  "community/paths/devotional-gatherings.html"
  "community/paths/study-circles.html"
  "data/community/index.json"
  "robots.txt"
  "sitemap.xml"
  "_headers"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$DEPLOY_DIR/$file" ]]; then
    echo "❌ Missing required deployment file: $file"
    exit 1
  fi
done

echo "✅ Required deployment files present."

echo
echo "===== DEPLOYMENT SUMMARY ====="

printf 'Files:  '
find "$DEPLOY_DIR" -type f | wc -l

printf 'Assets: '
find "$DEPLOY_DIR/assets" -type f | wc -l

echo
echo "✅ Deployment package built successfully."
echo "Nothing has been uploaded."
