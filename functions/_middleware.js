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

async function notFound({ request, env }) {
  const page = await env.ASSETS.fetch(new URL('/404', request.url));
  return new Response(page.ok ? page.body : 'Not found', {
    status: 404,
    headers: { 'Content-Type': page.ok ? 'text/html; charset=utf-8' : 'text/plain; charset=utf-8' },
  });
}

export async function onRequest(context) {
  let path;
  try {
    path = decode(new URL(context.request.url).pathname);
  } catch {
    return notFound(context);
  }
  if (/[\\\0]/.test(path) || path.split('/').includes('..') || BLOCKED.test(path)) {
    return notFound(context);
  }
  return context.next();
}
