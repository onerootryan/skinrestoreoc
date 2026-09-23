#!/usr/bin/env python3
"""
Build ONE self-contained, clickable preview of the whole site.

Every page becomes a view inside a single HTML file. Internal links switch views
(with working back/forward via the URL hash), external links (Square booking,
Instagram) open normally. Images are embedded once and reused. A small review
toolbar steps through the pages in order.

    npm run build && python3 scripts/build-clickable-preview.py
"""
import re, json, base64, mimetypes, pathlib, html as H

DIST = pathlib.Path('dist')
OUT = pathlib.Path('/mnt/user-data/outputs/skinrestore-full-site-preview.html')

ORDER = ['/', '/treatments',
         '/diamondglow', '/microchanneling', '/rf-skin-tightening', '/oxygen-facial',
         '/cryo-facial', '/teen-facial', '/dermaplaning', '/chemical-peels',
         '/biorepeel', '/back-facial', '/brow-tint',
         '/about', '/contact', '/thank-you']

def route_of(p):
    return '/' if p.stem == 'index' else '/' + p.stem

pages = {route_of(p): p.read_text() for p in DIST.glob('*.html')}
missing = [r for r in ORDER if r not in pages]
extra = [r for r in pages if r not in ORDER]
assert not missing, f'ORDER lists pages that were not built: {missing}'
assert not extra, f'built pages missing from ORDER (would be unreachable in toolbar): {extra}'

# ---- CSS: every linked chunk AND every inline <style>, from every page ----
css_parts, seen = [], set()
for src in pages.values():
    head = src.split('</head>')[0]
    for href in re.findall(r'<link rel="stylesheet" href="(/_astro/[^"]+\.css)"', head):
        if href not in seen:
            seen.add(href); css_parts.append((DIST / href.lstrip('/')).read_text())
    for block in re.findall(r'<style[^>]*>(.*?)</style>', head, re.S):
        if block not in seen:
            seen.add(block); css_parts.append(block)

# ---- Shell: nav + footer from the homepage (identical on every page) ----
# Take the shell from a normal page; the preview adds the overlay header on Home.
shell_src = pages['/treatments']
nav = re.search(r'<header class="nav[^"]*".*?</header>', shell_src, re.S).group(0)
footer = re.search(r'<footer class="ft".*?</footer>', shell_src, re.S).group(0)
assert 'nav--overlay' not in nav.split('>')[0], 'shell nav should not start in overlay mode'

# ---- Views: each page's <main> content ----
views, titles = [], {}
for r in ORDER:
    src = pages[r]
    titles[r] = H.unescape(re.search(r'<title>(.*?)</title>', src).group(1))
    main = re.search(r'<main id="main"[^>]*>(.*)</main>', src, re.S).group(1)
    views.append(f'<div class="pv-view" data-route="{r}" hidden>{main}</div>')
body = '\n'.join(views)

# ---- Images: embed each unique file once, reference by key ----
shell = nav + body + footer
img_keys = sorted(set(re.findall(r'src="/images/([^"]+)"', shell)))
images = {}
for k in img_keys:
    f = DIST / 'images' / k
    mime = mimetypes.guess_type(f.name)[0] or 'image/jpeg'
    images[k] = f'data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}'
def swap(m): return f'data-pv-img="{m.group(1)}"'
nav, body, footer = (re.sub(r'src="/images/([^"]+)"', swap, x) for x in (nav, body, footer))

labels = {r: titles[r].split(' | ')[0] for r in ORDER}
labels['/'] = 'Home'

doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{H.escape(titles['/'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Inter:wght@400;500;600&display=swap">
<style>{"".join(css_parts)}</style>
<style>
  /* ---- preview-only chrome ---- */
  html {{ scroll-padding-top: calc(6rem + env(safe-area-inset-top, 0px)); }}
  body {{ padding-bottom: calc(4.2rem + env(safe-area-inset-bottom, 0px)); }}
  header.nav {{ padding-top: env(safe-area-inset-top, 0px); }}
  .pv-bar {{
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 200;
    display: flex; align-items: center; gap: .6rem; justify-content: center; flex-wrap: wrap;
    padding: .55rem 1rem calc(.55rem + env(safe-area-inset-bottom, 0px));
    background: rgba(22,33,43,.94); color: #fff; font: 500 13px/1.2 Inter, system-ui, sans-serif;
    backdrop-filter: blur(6px);
  }}
  .pv-bar__tag {{ opacity: .7; letter-spacing: .04em; }}
  .pv-bar button, .pv-bar select {{
    font: inherit; color: #fff; background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.25); border-radius: 3px; padding: .35rem .7rem; cursor: pointer;
  }}
  .pv-bar select {{ max-width: 15rem; }}
  .pv-bar select option {{ color: #16212B; }}
  .pv-bar button:disabled {{ opacity: .35; cursor: default; }}
  .pv-bar__count {{ opacity: .7; min-width: 3.2rem; text-align: center; }}
  .pv-toast {{
    position: fixed; left: 50%; bottom: 5rem; transform: translateX(-50%); z-index: 210;
    background: #16212B; color: #fff; padding: .7rem 1rem; border-radius: 4px;
    font: 14px/1.4 Inter, system-ui, sans-serif; max-width: 90vw; display: none;
  }}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{nav}
<main id="main">{body}</main>
{footer}

<div class="pv-toast" id="pvToast" role="status"></div>
<nav class="pv-bar" aria-label="Preview pages">
  <span class="pv-bar__tag">PREVIEW</span>
  <button type="button" id="pvPrev" aria-label="Previous page">&larr; Prev</button>
  <select id="pvSelect" aria-label="Jump to page">
    {''.join(f'<option value="{r}">{H.escape(labels[r])}</option>' for r in ORDER)}
  </select>
  <span class="pv-bar__count" id="pvCount"></span>
  <button type="button" id="pvNext" aria-label="Next page">Next &rarr;</button>
</nav>

<script>
(() => {{
  const IMAGES = {json.dumps(images)};
  const TITLES = {json.dumps(titles)};
  const ORDER  = {json.dumps(ORDER)};

  document.querySelectorAll('[data-pv-img]').forEach(img => {{
    const src = IMAGES[img.getAttribute('data-pv-img')];
    if (src) img.src = src;
  }});

  const views = Object.fromEntries(
    [...document.querySelectorAll('.pv-view')].map(v => [v.dataset.route, v]));
  const sel = document.getElementById('pvSelect');
  const prev = document.getElementById('pvPrev');
  const next = document.getElementById('pvNext');
  const count = document.getElementById('pvCount');

  const norm = (p) => (p || '/').replace(/\\/+$/, '') || '/';

  function show(route, fromHash) {{
    route = views[norm(route)] ? norm(route) : '/';
    for (const [r, v] of Object.entries(views)) v.hidden = (r !== route);
    document.title = TITLES[route];
    // close any open menus
    document.querySelectorAll('details[open]').forEach(d => {{
      if (!d.closest('.pv-view') || d.closest('.nav')) d.open = false;
    }});
    const cb = document.getElementById('navtoggle'); if (cb) cb.checked = false;
    // transparent header over the photo on the homepage only
    const hdr = document.querySelector('header.nav');
    if (hdr) hdr.classList.toggle('nav--overlay', route === '/');
    // current-page highlighting in the nav
    document.querySelectorAll('.nav a[href^="/"]').forEach(a => {{
      if (norm(a.getAttribute('href')) === route) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    }});
    const i = ORDER.indexOf(route);
    sel.value = route; count.textContent = (i + 1) + ' / ' + ORDER.length;
    prev.disabled = i <= 0; next.disabled = i >= ORDER.length - 1;
    if (!fromHash) location.hash = '#' + route;
    window.scrollTo(0, 0);
    if (window.__navUpdate) window.__navUpdate();
  }}

  // internal links switch views; everything else behaves normally
  document.addEventListener('click', (e) => {{
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    if (href.startsWith('/') && views[norm(href)]) {{ e.preventDefault(); show(href); }}
  }});

  // the contact form only works once deployed on Netlify
  document.querySelectorAll('form').forEach(f => f.addEventListener('submit', (e) => {{
    e.preventDefault();
    const t = document.getElementById('pvToast');
    t.textContent = 'The contact form goes live once the site is deployed on Netlify.';
    t.style.display = 'block'; setTimeout(() => t.style.display = 'none', 3500);
  }}));

  sel.addEventListener('change', () => show(sel.value));
  prev.addEventListener('click', () => show(ORDER[ORDER.indexOf(sel.value) - 1]));
  next.addEventListener('click', () => show(ORDER[ORDER.indexOf(sel.value) + 1]));
  window.addEventListener('hashchange', () => show(location.hash.slice(1), true));

  show(location.hash.slice(1) || '/', true);
}})();
</script>
</body>
</html>'''

OUT.write_text(doc)
print(f'{OUT.name}: {len(doc)/1024/1024:.2f} MB · {len(ORDER)} pages · {len(images)} images embedded once · {len(css_parts)} style blocks')
