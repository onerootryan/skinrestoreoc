#!/usr/bin/env python3
"""
Build src/data/treatments.json from skin-restore-service-pages.md.

The markdown file stays the single source of truth for treatment copy.
Editorial notes (the > callouts, "Links to add", "⚙️" sections) are stripped;
"Links to add" is reused as the related-treatments list; FAQs become
structured data for FAQPage schema.

Usage:  python3 scripts/build-treatments.py path/to/skin-restore-service-pages.md
"""
import json, re, sys, pathlib
import markdown

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'content/skin-restore-service-pages.md')
OUT = pathlib.Path('src/data/treatments.json')

# ---- Per-page settings that don't belong in the copy file -----------------
# image: stand-in until treatment-specific photos arrive (one-line swap).
# desc:  meta descriptions rewritten for Netlify (~155 chars, no price talk).
META = {
    'diamondglow': dict(
        name='DiamondGlow', image='treatment-room.jpg', service='Facial treatment',
        desc='DiamondGlow facial in San Clemente — exfoliation, extraction and serum infusion in one treatment, with five serum options and no downtime.'),
    'microchanneling': dict(
        name='Micro Channeling', image='microchanneling.jpg', service='Collagen induction treatment',
        alt='A microchanneling pen being used during a nano needling treatment',
        desc='Microchanneling, also called nano needling, in San Clemente. Stimulates your own collagen and drives growth factor serums deeper. Little downtime.'),
    'rf-skin-tightening': dict(
        name='Wonder Touch RF', image='wonder-touch.jpg', service='Radiofrequency skin tightening',
        alt='A facial treatment being performed with a slow, massage-like technique',
        desc='Wonder Touch radiofrequency skin tightening in San Clemente. Firms, lifts and smooths without surgery, needles or downtime. Results build over a series.'),
    'oxygen-facial': dict(
        name='BREEZE Cryo Oxygen', image='breeze-treatment.jpg', service='Oxygen facial',
        alt='A client resting during a facial treatment in the studio at Skin Restore, San Clemente',
        desc='BREEZE needle-free oxygen facial in San Clemente — pressurized air infuses actives with lymphatic drainage and exfoliation. Comfortable, no downtime.'),
    'cryo-facial': dict(
        name='Cool Restore Cryo', image='cool-restore.jpg', service='Cryotherapy facial',
        alt='A Cool Restore cryo treatment being applied to a client\'s face at Skin Restore, San Clemente',
        desc='Cool Restore cryo facial in San Clemente. Controlled cooling firms skin, reduces puffiness and calms redness. No downtime — the one to book before an event.'),
    'dermaplaning': dict(
        name='DermaPlane', image='treatment-room.jpg', service='Dermaplaning',
        desc='Dermaplaning in San Clemente and Orange County. Removes dead skin and fine vellus hair for a smooth, bright finish. Standalone treatment or add-on.'),
    'chemical-peels': dict(
        name='Chemical Peels', image='chemical-peel.jpg', service='Chemical peel',
        alt='A client resting during a chemical peel appointment at Skin Restore, San Clemente',
        desc='Mild to moderate chemical peels in San Clemente for tone, texture and pigmentation — customized to your skin by a licensed esthetician.'),
    'teen-facial': dict(
        name='Teen Facial', image='treatment-room.jpg', service='Teen facial',
        desc='Teen facials in San Clemente — gentle, acne-focused treatment with safe professional extractions and a simple home routine. Parents welcome.'),
    'back-facial': dict(
        name='Back Facial', image='treatment-room.jpg', service='Back facial',
        desc='Back facial in San Clemente — deep cleansing, extractions and a treatment mask for back breakouts, congestion and rough texture. No downtime.'),
    'brow-tint': dict(
        name='Brow Tint', image='front-desk.jpg', service='Eyebrow tinting',
        desc='Brow tinting in San Clemente — fuller-looking, defined brows in about fifteen minutes, with the shade matched to your coloring. By appointment.'),
    'biorepeel': dict(
        name='BioRePeel', image='spa-hall.jpg', service='Chemical peel',
        desc='BioRePeel in San Clemente — a 35% TCA biphasic peel that renews skin with minimal visible peeling. For texture, tone, acne marks and fine lines.'),
}

EDITORIAL_LINE = re.compile(r'^\s*(>|\*\*Links to add:\*\*|\*\*Image alt text:\*\*|\*\*\[Book|\*\*Page name:|\*\*URL:|\*\*SEO)')
md = markdown.Markdown(extensions=['extra', 'sane_lists'])


def to_html(text: str) -> str:
    md.reset()
    return md.convert(text.strip())


def clean(body: str) -> str:
    return '\n'.join(l for l in body.splitlines() if not EDITORIAL_LINE.match(l)).strip()


def parse_faqs(body: str):
    faqs, q, a = [], None, []
    for line in body.splitlines():
        m = re.match(r'^\*\*(.+\?)\*\*\s*$', line.strip())
        if m:
            if q: faqs.append({'q': q, 'a': ' '.join(a).strip()})
            q, a = m.group(1).strip(), []
        elif q and line.strip():
            a.append(line.strip())
    if q: faqs.append({'q': q, 'a': ' '.join(a).strip()})
    return faqs


def parse_page(block: str):
    slug_m = re.search(r'\*\*URL:\*\*\s*`/([^`]+)`', block)
    if not slug_m:
        return None
    slug = slug_m.group(1).strip()
    if slug not in META:
        return None

    title_m = re.search(r'\*\*SEO title:\*\*\s*(.+)', block)
    alt_m = re.search(r'\*\*Image alt text:\*\*\s*"([^"]+)"', block)
    links_m = re.search(r'\*\*Links to add:\*\*(.+)', block)

    # A page ends at the next top-level heading ('# PART 3', '## ADD TO ...'),
    # otherwise the final page swallows the rest of the file.
    block = re.split(r'\n#{1,2} ', '\n' + block)[1] if block.startswith('#') else re.split(r'\n#{1,2} ', block)[0]
    # Drop everything from an editorial "⚙️" section onward
    block = re.split(r'\n###\s*⚙', block)[0]

    parts = re.split(r'\n###\s*(H1|H2):\s*', '\n' + block)
    h1, intro, sections, faqs = '', '', [], []
    for i in range(1, len(parts) - 1, 2):
        kind, rest = parts[i], parts[i + 1]
        heading, _, body = rest.partition('\n')
        heading, body = heading.strip(), clean(body)
        if kind == 'H1':
            h1, intro = heading, to_html(body)
        elif heading.lower().startswith('common questions'):
            faqs = parse_faqs(body)
        elif heading.lower().startswith('book'):
            continue   # rendered as a proper CTA by the template
        elif body:
            sections.append({'h2': heading, 'html': to_html(body)})

    related = []
    if links_m:
        for s in re.findall(r'`/([a-z0-9-]+)`', links_m.group(1)):
            if s in META and s != slug and s not in related:
                related.append(s)

    m = META[slug]
    return {
        'slug': slug,
        'name': m['name'],
        'serviceType': m['service'],
        'title': (title_m.group(1).strip() if title_m else m['name']),
        'description': m['desc'],
        'image': m['image'],
        'alt': m.get('alt') or (alt_m.group(1) if alt_m else f"{m['name']} at Skin Restore, San Clemente"),
        'h1': h1,
        'intro': intro,
        'sections': sections,
        'faqs': faqs,
        'related': related,
    }


def main():
    text = SRC.read_text()
    blocks = re.split(r'\n## PAGE \d+ — ', text)
    pages = [p for p in (parse_page(b) for b in blocks) if p]
    # ---- Guard: private / editorial material must never reach a public page ----
    FORBIDDEN = [
        r'\$\d',                    # any price
        r'internal reference',
        r'Before you publish',
        r'Barbering and Cosmetology holds',
        r'liability insurer',
        r'PART \d',
        r'searches/month|/mo\b|difficulty \d',
        r'YOUR PRICE|TODO',
    ]
    for p in pages:
        text = json.dumps(p)
        for pat in FORBIDDEN:
            if re.search(pat, text, re.I):
                raise SystemExit(f"BLOCKED: '{pat}' found in public page /{p['slug']} — not writing output")
    OUT.write_text(json.dumps(pages, indent=2, ensure_ascii=False))
    for p in pages:
        print(f"{p['slug']:22} sections:{len(p['sections']):2}  faqs:{len(p['faqs']):2}  related:{p['related']}")
    missing = set(META) - {p['slug'] for p in pages}
    if missing:
        raise SystemExit(f'missing pages: {missing}')
    print(f'\n{len(pages)} treatments → {OUT}')


if __name__ == '__main__':
    main()
