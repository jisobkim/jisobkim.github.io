# Weaverlet 소개 페이지를 언어마다 정적 HTML로 만든다: python3 weaverlet-src/build.py
# page.html(영어·한국어 원문)을 고친 뒤 다시 돌려 public/weaverlet/ 아래 결과까지 커밋한다.
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "public" / "weaverlet"
SITE = "https://qn51z.com/weaverlet/"
LANGS = ["en", "ko", "ja", "zh-Hans", "es", "vi", "ms", "id", "pt-BR", "th", "ru", "fr", "de", "it", "hi"]
OG_LOCALE = {
    "en": "en_US", "ko": "ko_KR", "ja": "ja_JP", "zh-Hans": "zh_CN", "es": "es_ES", "vi": "vi_VN", "ms": "ms_MY",
    "id": "id_ID", "pt-BR": "pt_BR", "th": "th_TH", "ru": "ru_RU", "fr": "fr_FR", "de": "de_DE", "it": "it_IT", "hi": "hi_IN",
}
EN_META = {
    "__title": "Weaverlet: Markdown notes for the Mac",
    "__description": "Weaverlet opens the Markdown folder you already have. Wikilinks, backlinks, Mermaid, fast search and viewers for PDF and office files. No import, no account.",
    "__og_description": "Open the Markdown folder you already have. No import, no account.",
    "__lang_name": "English",
}
PAIR = re.compile(r'<span lang="en">(.*?)</span>(\s*)<span lang="ko">(.*?)</span>', re.S)


def url(lang: str) -> str:
    return SITE if lang == "en" else f"{SITE}{lang.lower()}/"


def page(lang: str, tpl: str, t: dict) -> str:
    def pair(m: re.Match) -> str:
        if lang == "en":
            return m[1]
        if lang == "ko":
            return m[3]
        return t[m[1]]

    body = PAIR.sub(pair, tpl)
    if lang != "en":
        body = re.sub(r'(alt|aria-label)="([^"]+)"', lambda m: f'{m[1]}="{html.escape(t.get(m[2], m[2]))}"', body)
    body = re.sub(r'(src|href|poster)="(img/|support/|privacy/)', r'\1="/weaverlet/\2', body)
    body = body.replace('href="./"', f'href="{url(lang)}"').replace("{{lang}}", lang)

    e = html.escape
    alternates = "".join(f'<link rel="alternate" hreflang="{l}" href="{url(l)}">\n' for l in LANGS)
    og_img = SITE + "img/og-image-1200x630" + ("-ko" if lang == "ko" else "") + ".png"
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Weaverlet",
        "description": t["__description"],
        "inLanguage": lang,
        "operatingSystem": "macOS 12 or later",
        "applicationCategory": "UtilitiesApplication",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "downloadUrl": "https://apps.apple.com/app/id6833345636",
        "url": url(lang),
        "image": og_img,
    }
    head = (
        f"<title>{e(t['__title'])}</title>\n"
        f'<meta name="description" content="{e(t["__description"])}">\n'
        f'<link rel="canonical" href="{url(lang)}">\n'
        f"{alternates}"
        f'<link rel="alternate" hreflang="x-default" href="{SITE}">\n'
        f'<meta property="og:type" content="website">\n'
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}">\n'
        f'<meta property="og:title" content="{e(t["__title"])}">\n'
        f'<meta property="og:description" content="{e(t["__og_description"])}">\n'
        f'<meta property="og:image" content="{og_img}">\n'
        f'<meta property="og:url" content="{url(lang)}">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
    )
    return body.replace("<!--HEAD-->\n", head).replace("<!--LANG-->", picker(lang))


def picker(lang: str) -> str:
    names = {l: (EN_META if l == "en" else I18N[l])["__lang_name"] for l in LANGS}
    opts = "".join(
        f'<option value="{l}" data-href="{url(l)}"{" selected" if l == lang else ""}>{html.escape(names[l])}</option>'
        for l in LANGS
    )
    return f'<select class="lang" aria-label="Language">{opts}</select>'


I18N = json.loads((ROOT / "i18n.json").read_text())

if __name__ == "__main__":
    tpl = (ROOT / "page.html").read_text()
    for lang in LANGS:
        out = OUT / ("" if lang == "en" else lang.lower()) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang, tpl, EN_META if lang == "en" else I18N[lang]))
        print(out.relative_to(OUT.parent.parent))
