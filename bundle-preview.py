#!/usr/bin/env python3
"""
Bundle built pages into self-contained HTML for preview artifacts.

Inlines EVERY local stylesheet (Astro emits one per component chunk, so there
can be several) and every local image as a data URI. Verifies nothing local is
left pointing outward before writing.
"""
import re, base64, pathlib, mimetypes, sys

DIST = pathlib.Path('dist')
OUT = pathlib.Path('/mnt/user-data/outputs')

PAGES = [
    ('index.html',    'skinrestore-homepage-preview.html'),
    ('treatments.html', 'skinrestore-treatments-preview.html'),
    ('contact.html',  'skinrestore-contact-preview.html'),
    ('about.html',    'skinrestore-about-preview.html'),
    ('diamondglow.html',     'skinrestore-diamondglow-preview.html'),
    ('microchanneling.html', 'skinrestore-microchanneling-preview.html'),
    ('teen-facial.html',     'skinrestore-teen-facial-preview.html'),
    ('back-facial.html',     'skinrestore-back-facial-preview.html'),
    ('brow-tint.html',       'skinrestore-brow-tint-preview.html'),
    ('biorepeel.html',       'skinrestore-biorepeel-preview.html'),
]


def bundle(page: str) -> str:
    html = (DIST / page).read_text()

    # --- all local stylesheets, not just the first ---
    def css(match):
        href = match.group(1)
        f = DIST / href.lstrip('/')
        if not f.exists():
            print(f'  ! missing css {href}', file=sys.stderr)
            return match.group(0)
        return f'<style>{f.read_text()}</style>'

    html = re.sub(r'<link\s+rel="stylesheet"\s+href="(/[^"]+\.css)"[^>]*>', css, html)

    # --- all local images ---
    def img(match):
        src = match.group(1)
        f = DIST / src.lstrip('/')
        if not f.exists():
            print(f'  ! missing image {src}', file=sys.stderr)
            return match.group(0)
        mime = mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
        return f'src="data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"'

    html = re.sub(r'src="(/[^"]+\.(?:jpg|jpeg|png|svg|webp|avif|gif))"', img, html)

    # --- verify ---
    leftover_css = re.findall(r'<link[^>]+href="/[^"]+\.css"', html)
    leftover_img = re.findall(r'src="/[^"]+\.(?:jpg|jpeg|png|svg|webp)"', html)
    if leftover_css or leftover_img:
        raise SystemExit(f'{page}: unresolved local refs — css:{leftover_css} img:{leftover_img}')
    return html


if __name__ == '__main__':
    for page, out in PAGES:
        if not (DIST / page).exists():
            continue
        h = bundle(page)
        (OUT / out).write_text(h)
        print(f'{out:42} {len(h)/1024/1024:.2f} MB  ok')
