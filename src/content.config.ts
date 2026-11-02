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
    // Image in /public/images, e.g. "/images/diamondglow.jpg". Must exist.
    image: z
      .string()
      .regex(/^\/images\/[\w.-]+\.(jpe?g|png|webp)$/)
      .refine((p) => existsSync(`./public${p}`), { message: 'Image not found in public/images' })
      .optional(),
    imageAlt: z.string().optional(),
    // Treatment pages this post supports — shown as cards and linked. Slugs from treatments.json.
    treatments: z.array(z.enum(treatmentSlugs)).max(3).default([]),
    tags: z.array(z.string()).default([]),
    faqs: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
    // Only set when Demi has actually read and approved the post.
    reviewedByDemi: z.boolean().default(false),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
