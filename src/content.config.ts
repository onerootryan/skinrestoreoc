// Blog posts live in src/content/blog/*.md — one file per post.
// The schema below is a guardrail: the build fails (and Netlify keeps the
// last good deploy) if a post links a treatment that doesn't exist, points
// at a missing image, or has an over-long title/description.
import { existsSync } from 'node:fs';
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import treatments from './data/treatments.json';

const treatmentSlugs = treatments.map((t) => t.slug) as [string, ...string[]];

const blog = defineCollection({
  // Files starting with "_" are ignored (handy for templates/notes).
  loader: glob({ pattern: '[!_]*.md', base: './src/content/blog' }),
  schema: z.object({
    // Keyword-led headline shown on the page (<h1>).
    title: z.string().min(10).max(80),
    // Optional shorter <title> tag; " | Skin Restore" is appended. Keep ≤ 60 with the suffix.
    seoTitle: z.string().max(46).optional(),
    // Meta description and the excerpt on /blog.
    description: z.string().min(70).max(160),
    publishDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    // Either a local image in /public/images (e.g. "/images/diamondglow.jpg", must exist),
    // a hotlinked Unsplash photo (https://images.unsplash.com/..., per Unsplash's API rules),
    // or a licensed stock photo hosted in Skin Restore's Cloudinary account.
    image: z
      .string()
      .refine(
        (p) =>
          /^\/images\/[\w.-]+\.(jpe?g|png|webp)$/.test(p)
            ? existsSync(`./public${p}`)
            : /^https:\/\/(images\.unsplash\.com|res\.cloudinary\.com\/x2sxptbc)\//.test(p),
        { message: 'Image must exist in public/images, or be an images.unsplash.com / Skin Restore Cloudinary URL' },
      )
      .optional(),
    imageAlt: z.string().optional(),
    // Required for stock photos: shown under the image ("Photo by <name> on <source>").
    imageCredit: z
      .object({
        name: z.string(),
        url: z.string().url().optional(),
        source: z.enum(['Unsplash', 'Adobe Stock', 'Shutterstock']),
        sourceUrl: z.string().url().optional(),
      })
      .optional(),
    // Treatment pages this post supports — shown as cards and linked. Slugs from treatments.json.
    treatments: z.array(z.enum(treatmentSlugs)).max(3).default([]),
    tags: z.array(z.string()).default([]),
    faqs: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
    // Only set when Demi has actually read and approved the post.
    reviewedByDemi: z.boolean().default(false),
    draft: z.boolean().default(false),
  }).refine((d) => !d.image?.startsWith('https://') || d.imageCredit, {
    message: 'Stock photos (remote image URLs) need an imageCredit',
    path: ['imageCredit'],
  }),
});

export const collections = { blog };
