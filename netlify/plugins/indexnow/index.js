// Pings IndexNow (Bing, Yandex, Seznam, Naver...) with the pages that changed
// in this deploy, so search engines re-crawl them right away instead of waiting.
// Only runs on production deploys. Never fails the build.
import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

const KEY = '5d19b2f53f53260fff41f22bffe2f2ef';
const HOST = 'www.skinrestoreoc.com';
const SITE = `https://${HOST}`;
const CACHE_FILE = '.indexnow-hashes.json';

async function sitemapUrls(publishDir) {
  const files = (await readdir(publishDir)).filter((f) => /^sitemap-\d+\.xml$/.test(f));
  const urls = [];
  for (const f of files) {
    const xml = await readFile(join(publishDir, f), 'utf8');
    for (const m of xml.matchAll(/<loc>([^<]+)<\/loc>/g)) urls.push(m[1]);
  }
  return urls;
}

// Map a public URL to its built file (build.format is 'file': /about -> about.html).
function fileFor(publishDir, url) {
  const path = new URL(url).pathname.replace(/\/$/, '');
  return join(publishDir, path === '' ? 'index.html' : `${path}.html`);
}

export const onSuccess = async ({ constants, utils }) => {
  try {
    if (process.env.CONTEXT !== 'production') {
      console.log('IndexNow: skipped (not a production deploy)');
      return;
    }
    const dir = constants.PUBLISH_DIR;
    const urls = await sitemapUrls(dir);
    const hashes = {};
    for (const url of urls) {
      try {
        hashes[url] = createHash('sha1').update(await readFile(fileFor(dir, url))).digest('hex');
      } catch {
        hashes[url] = null;
      }
    }

    let previous = {};
    if (await utils.cache.restore(CACHE_FILE)) {
      previous = JSON.parse(await readFile(CACHE_FILE, 'utf8'));
    }
    const changed = urls.filter((u) => !hashes[u] || hashes[u] !== previous[u]);
    if (!changed.length) {
      console.log('IndexNow: no changed pages');
      return;
    }

    const res = await fetch('https://api.indexnow.org/indexnow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ host: HOST, key: KEY, keyLocation: `${SITE}/${KEY}.txt`, urlList: changed }),
    });
    console.log(`IndexNow: submitted ${changed.length} URL(s), HTTP ${res.status}`);
    if (res.ok) {
      const { writeFile } = await import('node:fs/promises');
      await writeFile(CACHE_FILE, JSON.stringify(hashes));
      await utils.cache.save(CACHE_FILE);
    }
  } catch (err) {
    console.log(`IndexNow: skipped (${err.message})`);
  }
};
