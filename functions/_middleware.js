// Cloudflare Pages serves every committed file. This returns 404 for the files that are not
// part of the site: docs, prompts, generator scripts and seed data.
const BLOCKED = /^\/(tools|data)(\/|$)|\.(md|py|pyc)\/?$/i;

function decode(path) {
  for (let i = 0; i < 3; i++) {
    const next = decodeURIComponent(path);
    if (next === path) break;
    path = next;
  }
  return path;
}

export async function onRequest({ request, next }) {
  let path;
  try {
    path = decode(new URL(request.url).pathname);
  } catch {
    return new Response('Not found', { status: 404 });
  }
  if (/[\\\0]/.test(path) || path.split('/').includes('..') || BLOCKED.test(path)) {
    return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  }
  return next();
}
