from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import URLError
import re
import subprocess
import tempfile

PAGE = Path("pages/community/experiences/social-action-experiences.html")
CSS = Path("styles/community-path.css")
ASSETS = Path("assets/community/social-action")

SOURCES = {
    "ghana": "https://news.bahai.org/story/1795/ghana-olinga-foundation-fosters-literacy-with-moral-purpose",
    "zambia": "https://news.bahai.org/podcasts/insights-from-the-field/1796/insights-field-educational-initiatives-zambia-empower-communities-reshape-future",
    "colombia": "https://news.bahai.org/story/1811/colombia-new-film-highlights-efforts-toward-environmental-restoration",
    "congo": "https://news.bahai.org/story/1475/clinic-drc-causes-disease-promotes-discourse-health",
    "india": "https://news.bahai.org/story/176/backgrounder-barli-development-institute-rural-women",
    "ecuador": "https://news.bahai.org/story/1855/ecuador-indigenous-families-foster-hope-artistic-expression",
    "nicaragua": "https://news.bahai.org/story/1422/community-banks-nicaragua-early-precautions",
    "mozambique": None,
    "agriculture-colombia": "https://news.bahai.org/story/1445/self-sufficiency-fundaec-local-food-production",
    "agriculture-nepal": "https://news.bahai.org/story/1437/nepalese-village-agricultural-capacity-long-term",
    "agriculture-vanuatu": "https://news.bahai.org/story/1414/providing-food-security-global-health-crisis",
    "agriculture-uganda": "https://news.bahai.org/story/1414/providing-food-security-global-health-crisis",
    "agriculture-congo": "https://news.bahai.org/podcasts/in-conversation/1863/in-conversation-fostering-collective-action-canjavu-village",
}

class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.meta = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)

        if tag == "meta":
            if a.get("property") in ("og:image", "og:image:url"):
                self.meta.append(a.get("content", ""))

        if tag == "img":
            self.images.append({
                "src": a.get("src", ""),
                "alt": a.get("alt", ""),
            })

def fetch(url):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,image/*",
    })
    with urlopen(req, timeout=25) as response:
        return response.read()

def get_image_candidates(url, key):
    parser = ImageParser()
    parser.feed(fetch(url).decode("utf-8", errors="replace"))

    images = [
        (urljoin(url, x["src"]), x["alt"])
        for x in parser.images
        if x["src"]
    ]

    # Prefer images with a subject-relevant caption/alt.
    terms = {
        "agriculture-colombia": ["farm", "crop", "plant", "seed", "garden"],
        "agriculture-nepal": ["irrigation", "village", "agricultur"],
        "agriculture-vanuatu": ["nursery", "seedling", "agricultur"],
        "agriculture-uganda": ["radio", "uganda"],
        "agriculture-congo": ["canjavu", "agricultur"],
    }.get(key, [])

    def score(item):
        src, alt = item
        combined = (src + " " + alt).lower()
        return sum(3 for term in terms if term in combined)

    images.sort(key=score, reverse=True)

    candidates = images + [(urljoin(url, x), "") for x in parser.meta]

    # Remove duplicates.
    seen = set()
    result = []

    for src, alt in candidates:
        if src in seen:
            continue
        seen.add(src)

        if not src.startswith("https://"):
            continue

        if not (
            "datocms-assets.com" in urlparse(src).netloc
            or "news.bahai.org" in urlparse(src).netloc
        ):
            continue

        result.append((src, alt))

    return result

def image_valid(path):
    result = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return False

    widths = re.findall(r"pixelWidth:\s*(\d+)", result.stdout)
    heights = re.findall(r"pixelHeight:\s*(\d+)", result.stdout)

    return bool(
        widths and heights
        and int(widths[0]) >= 500
        and int(heights[0]) >= 250
    )

def download_image(url, destination):
    data = fetch(url)

    if len(data) < 10000:
        raise ValueError("Image too small")

    # This implementation stores JPEG photographs only.
    if not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("Not a JPEG")

    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "original.jpg"
        original.write_bytes(data)

        if not image_valid(original):
            raise ValueError("Invalid image dimensions")

        result = subprocess.run(
            ["sips", "-Z", "1200", "-s", "format", "jpeg",
             str(original), "--out", str(destination)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise ValueError(result.stderr)

    return image_valid(destination)

html = PAGE.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")

if "social-action-documentary-photo" in html:
    raise SystemExit("Photographs already integrated. No changes made.")

ASSETS.mkdir(parents=True, exist_ok=True)

successful = {}
failed = {}

for key, source in SOURCES.items():
    if not source:
        failed[key] = "Original source URL not yet established"
        continue

    destination = ASSETS / f"{key}.jpg"

    try:
        candidates = get_image_candidates(source, key)

        for image_url, alt in candidates:
            try:
                if download_image(image_url, destination):
                    successful[key] = {
                        "source": source,
                        "image": image_url,
                        "alt": alt,
                    }
                    break
            except (ValueError, URLError, OSError):
                continue

        if key not in successful:
            failed[key] = "No suitable downloadable JPEG"

    except Exception as exc:
        failed[key] = str(exc)

print("\n===== DOWNLOADED PHOTOGRAPHS =====")
for key, info in successful.items():
    print(f"✓ {key}: {info['image']}")

print("\n===== SKIPPED =====")
for key, reason in failed.items():
    print(f"– {key}: {reason}")

def photo_markup(key):
    info = successful[key]

    return f'''
          <figure class="social-action-documentary-photo">
            <img
              src="/assets/community/social-action/{key}.jpg"
              alt="{escape(info["alt"] or "صورة من التقرير الأصلي", quote=True)}"
              loading="lazy"
              decoding="async">
            <figcaption>
              صورة منشورة مع التقرير الأصلي —
              <a href="{escape(info["source"], quote=True)}"
                 target="_blank"
                 rel="noopener noreferrer">
                خدمة أخبار العالم البهائي
              </a>
            </figcaption>
          </figure>
'''

# Integrate photographs into the eight existing experiences.
for key in [
    "ghana", "zambia", "colombia", "congo",
    "india", "ecuador", "nicaragua", "mozambique"
]:
    if key not in successful:
        continue

    pattern = re.compile(
        rf'(<article class="jy-experience" id="{key}">.*?'
        r'<div class="jy-card-media social-action-card-media">)',
        re.S
    )

    html, count = pattern.subn(
        lambda m: m.group(1) + photo_markup(key),
        html,
        count=1,
    )

    if count != 1:
        raise SystemExit(f"Could not locate original card: {key}")

# Integrate photographs into the five agriculture cards.
for key in [
    "agriculture-colombia",
    "agriculture-nepal",
    "agriculture-vanuatu",
    "agriculture-uganda",
    "agriculture-congo",
]:
    if key not in successful:
        continue

    pattern = re.compile(
        rf'(<article class="sa-evidence-card" id="{key}">\s*'
        r'<div class="sa-evidence-card-top">)',
        re.S
    )

    html, count = pattern.subn(
        lambda m: m.group(1) + photo_markup(key),
        html,
        count=1,
    )

    if count != 1:
        raise SystemExit(f"Could not locate agriculture card: {key}")

css_addition = '''

/* Social action — documentary photographs */

.social-action-experiences-page .social-action-documentary-photo {
  margin: 0;
  overflow: hidden;
}

.social-action-experiences-page .social-action-documentary-photo img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 3 / 2;
  object-fit: contain;
  background: #f4f1e9;
}

.social-action-experiences-page .social-action-documentary-photo figcaption {
  padding: .45rem .7rem;
  font-size: .75rem;
  line-height: 1.7;
  color: #59676b;
  background: #faf8f2;
}

.social-action-experiences-page .social-action-documentary-photo figcaption a {
  color: var(--teal);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.social-action-experiences-page .sa-evidence-card-top {
  padding-top: 0;
}

.social-action-experiences-page .sa-evidence-card-top
.social-action-documentary-photo {
  margin: 0 -1.5rem 1.5rem;
}

.social-action-experiences-page .jy-card-media.social-action-card-media {
  overflow: hidden;
}

.social-action-experiences-page .jy-card-media.social-action-card-media
.social-action-documentary-photo {
  width: 100%;
}

.social-action-experiences-page .jy-card-media.social-action-card-media
.social-action-documentary-photo img {
  max-height: 260px;
}
'''

if "Social action — documentary photographs" not in css:
    css += css_addition

PAGE.write_text(html, encoding="utf-8")
CSS.write_text(css, encoding="utf-8")

print(f"\n✓ Integrated {len(successful)} documentary photographs.")
print("✓ Existing experience descriptions preserved.")
print("✓ Original report links included in photograph credits.")
