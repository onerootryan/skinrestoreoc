#!/usr/bin/env python3
"""
Pre-launch check. Run before pointing skinrestoreoc.com at Netlify:

    python3 scripts/prelaunch-check.py

Exits non-zero if anything would break or embarrass the site on launch day.
BLOCKERS stop the launch. WARNINGS are worth fixing but won't break anything.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
biz = (ROOT / 'src/data/business.js').read_text()
home = (ROOT / 'src/pages/index.astro').read_text()
contact = (ROOT / 'src/pages/contact.astro').read_text()


def field(name):
    m = re.search(rf"^\s*{name}:\s*'([^']*)'", biz, re.M)
    return m.group(1) if m else ''


def num(name):
    m = re.search(rf"^\s*{name}:\s*(-?[\d.]+)", biz, re.M)
    return float(m.group(1)) if m else None


blockers, warnings = [], []

# --- Booking: the one that silently breaks every button on launch day ---
booking = field('bookingUrl')
if not booking or 'REPLACE-ME' in booking:
    blockers.append('bookingUrl is not set.')
elif 'skinrestoreoc.com' in booking:
    blockers.append(
        f'bookingUrl points at skinrestoreoc.com ({booking}).\n'
        '    That page lives on the Square Online site, which stops serving this\n'
        '    domain at cutover — every Book button would 404 after launch.\n'
        '    Use the standalone Square Appointments URL instead:\n'
        '    Square Dashboard > Appointments > Online Booking > Channels > Get URL')

# --- Map coordinates: placeholder values point Google at the wrong spot ---
if (num('lat'), num('lng')) == (33.4270, -117.6120):
    blockers.append('lat/lng are still placeholder coordinates — Google Maps and the\n'
                    '    LocalBusiness schema would pin the wrong location.\n'
                    '    Right-click your pin in Google Maps to copy the real ones.')

# --- Placeholder reviews on the homepage ---
if 'Add a real review here' in home or 'First name, last initial' in home:
    blockers.append('Homepage still shows placeholder review text.')

# --- Every page needs a .html -> clean-URL redirect (else duplicate content) ---
if (ROOT / 'dist' / 'index.html').exists():
    import tomllib
    froms = [r['from'] for r in tomllib.loads((ROOT / 'netlify.toml').read_bytes().decode()).get('redirects', [])]
    stems = [p.stem for p in (ROOT / 'dist').glob('*.html') if p.stem != 'index']
    missing_r = sorted(st for st in stems if f'/{st}.html' not in froms)
    if missing_r:
        blockers.append(f'Pages reachable at two URLs — no .html redirect in netlify.toml for: {missing_r}')

# --- Identifiable client photos need written consent before going public ---
if re.search(r'clientPhotoConsent:\s*false', biz):
    blockers.append('A photo of an identifiable client is used on the site (BREEZE page).\n'
                    '    Get written permission from that client, then set\n'
                    '    clientPhotoConsent: true in src/data/business.js.')

# --- Every treatment page must be listed in llms.txt (AI crawlers read it) ---
import json
treat = ROOT / 'src/data/treatments.json'
if treat.exists():
    slugs = {t['slug'] for t in json.loads(treat.read_text())}
    listed = set(re.findall(r'skinrestoreoc\.com/([a-z0-9-]+)\)', (ROOT / 'public/llms.txt').read_text()))
    if slugs - listed:
        warnings.append(f'Treatment pages missing from public/llms.txt: {sorted(slugs - listed)}')
    # ...and the reverse: llms.txt must not point AI assistants at pages that don't exist
    pages = {x.stem for x in (ROOT / 'src/pages').glob('*.astro') if not x.stem.startswith('[')}
    dead = sorted(listed - slugs - pages)
    if dead:
        blockers.append(f'public/llms.txt lists pages that do not exist: {dead}')

# --- Exactly one logo visible in every header state (needs a build in dist/) ---
import subprocess
if (ROOT / 'dist' / 'index.html').exists():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/check-logo-visibility.py')],
                       capture_output=True, text=True)
    if r.returncode != 0:
        bad = [l.strip() for l in r.stdout.splitlines() if l.startswith('FAIL')]
        blockers.append('Header logo shows incorrectly:\n    ' + '\n    '.join(bad))
else:
    warnings.append('No build in dist/ — run `npm run build` so the logo check can run.')

# --- Warnings: worth doing, won't break anything ---
if re.search(r"google:\s*''", biz):
    warnings.append('No Google Business Profile URL in business.social — worth adding to schema sameAs.')
if 'TODO: add parking' in contact:
    warnings.append('Contact page has no parking / suite / entrance guidance yet.')
if re.search(r'shopLive:\s*true', biz):
    llms = (ROOT / 'public/llms.txt').read_text()
    if 'skinrestorerx' not in llms:
        warnings.append('shopLive is on but public/llms.txt still omits skinrestorerx.com.')

print('\nSkin Restore — pre-launch check\n' + '=' * 34)
for b in blockers:
    print(f'✗ BLOCKER  {b}')
for w in warnings:
    print(f'! warning  {w}')
if not blockers and not warnings:
    print('✓ All clear.')
print()
if blockers:
    print(f'{len(blockers)} blocker(s). Do not launch yet.')
    sys.exit(1)
print('No blockers. Safe to launch.')
