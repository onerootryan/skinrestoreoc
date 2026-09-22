#!/usr/bin/env python3
"""
Which header logo is actually visible? Resolves the real CSS cascade
(specificity, then source order) for the `display` property, against the
compiled CSS — the thing a lightweight test DOM gets wrong.

    python3 scripts/check-logo-visibility.py        (exits 1 on failure)
"""
import pathlib, sys, re
import tinycss2, cssselect
from lxml import html as LH

DIST = pathlib.Path(__file__).resolve().parent.parent / 'dist'

def load_rules():
    css = ''.join(p.read_text() for p in sorted((DIST / '_astro').glob('*.css')))
    for page in DIST.glob('*.html'):
        css += ''.join(re.findall(r'<style[^>]*>(.*?)</style>', page.read_text(), re.S))
    rules, order = [], 0
    for r in tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True):
        if r.type != 'qualified-rule':
            continue            # @media etc. — the checks below are desktop-width
        decls = tinycss2.parse_declaration_list(r.content, skip_comments=True, skip_whitespace=True)
        disp = [tinycss2.serialize(d.value).strip() for d in decls
                if getattr(d, 'lower_name', '') == 'display']
        if not disp:
            continue
        for sel in tinycss2.serialize(r.prelude).split(','):
            sel = sel.strip()
            try:
                parsed = cssselect.parse(sel)[0]
                xp = cssselect.GenericTranslator().css_to_xpath(sel)
            except Exception:
                continue        # :has(), :hover etc. — states not under test
            order += 1
            rules.append((parsed.specificity(), order, xp, disp[-1], sel))
    return rules

def winner(el, rules):
    hits = [(spec, order, val) for spec, order, xp, val, _ in rules if el in el.getroottree().xpath(xp)]
    return max(hits)[2] if hits else 'inline(default)'

def visible_logos(page, extra_classes=''):
    tree = LH.fromstring((DIST / page).read_text())
    hdr = tree.xpath('//header[contains(concat(" ", normalize-space(@class), " "), " nav ")]')[0]
    if extra_classes:
        hdr.set('class', hdr.get('class') + ' ' + extra_classes)
    out = []
    for img in hdr.xpath('.//img'):
        if winner(img, RULES) != 'none':
            out.append('white' if 'nav__logo--light' in img.get('class', '') else 'dark')
    return out

RULES = load_rules()
cases = [
    ('index.html',       '',          ['white'], 'Home, top of page'),
    ('index.html',       'is-solid',  ['dark'],  'Home, scrolled'),
    ('treatments.html',  '',          ['dark'],  'Treatments'),
    ('oxygen-facial.html','',         ['dark'],  'Treatment page'),
    ('about.html',       '',          ['dark'],  'About'),
    ('contact.html',     '',          ['dark'],  'Contact'),
]
fail = False
for page, cls, want, label in cases:
    got = visible_logos(page, cls)
    ok = got == want; fail |= not ok
    print(f"{'ok  ' if ok else 'FAIL'} {label:20} visible: {' + '.join(got) or 'none'}")
sys.exit(1 if fail else 0)
