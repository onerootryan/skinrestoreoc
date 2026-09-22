# Skin Restore — skinrestoreoc.com

Static site built with Astro, deployed to Netlify from GitHub.
Replaces the Square Online site. Products live separately at skinrestorerx.com.
Booking is handled by Square Appointments (external link).

## Run locally

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # outputs to dist/
```

## Where things live

| What | Where |
|---|---|
| Business facts, phone, hours, booking URL | `src/data/business.js` |
| Colour, type, spacing tokens | `src/styles/global.css` |
| Page shell, meta tags, fonts | `src/layouts/Base.astro` |
| LocalBusiness / Service / FAQ schema | `src/components/Schema.astro` |
| Book buttons | `src/components/BookButton.astro` |
| Pages | `src/pages/` |
| AI-crawler summary | `public/llms.txt` |

**Edit `src/data/business.js` first.** Phone, hours, address and the booking URL
flow from there into every page *and* into the structured data. Nothing is hardcoded twice.

## Before launch — the TODOs

Search the repo for `TODO:` — there are five:

1. `business.js` — Square Appointments booking flow URL
   (Square Dashboard → Appointments → Online Booking → Channels → Get URL)
2. `business.js` — real lat/lng (right-click your pin in Google Maps)
3. `business.js` — confirm hours; must match Google Business Profile exactly
4. `business.js` — Google Business Profile / Instagram / Yelp URLs for `sameAs`
5. `index.astro` — two real Google reviews, and a treatment-room photo

## Design direction

Clinical calm, coastal light. Deliberately *not* the warm-cream-and-terracotta
default that every med spa site uses. Cool navy ink (`--ink`), cool white ground,
the existing brand blue-grey (`#99ADC1`) carried over from the Square site, deep
marine as the action colour. One display serif (Newsreader) plus one grotesque
(Schibsted Grotesk). Left-aligned throughout.

The deliberate feature is the credentials strip under the hero — licence number,
years, former role — treated as structure rather than decoration, because
verifiable credentials are the actual differentiator.

## Deploy

Netlify picks up `netlify.toml`: `npm run build`, publish `dist`.
Netlify handles HTTPS automatically, which also fixes the `http://www`
duplicate-content issue the Ahrefs audit found on the Square site.

## Old Square URLs

The 44 `/product/*` and 6 `/shop/*` URLs are intentionally **not** carried over
and will 404. The audit confirmed all of them have zero organic traffic, zero
backlinks and zero referring domains. No redirects needed.
