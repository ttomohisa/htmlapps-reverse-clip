// Reverse Clip PR-Preview-only selective cross-origin isolation.
// ST root remains unchanged; MT must have COOP/COEP for SharedArrayBuffer.
// This Worker does not fetch user media, contact APIs, or alter HTML contents.
const ISOLATED_ROUTES = new Set([
  '/index.mt.html',
  '/index.mt.self-extract.html',
]);
export default {
  async fetch(request, env) {
    const pathname = new URL(request.url).pathname;
    const asset = await env.ASSETS.fetch(request);
    if (asset.status !== 200) return asset;
    const response = new Response(asset.body, asset);
    response.headers.set('X-RC-Preview-Worker', 'active');
    if (!ISOLATED_ROUTES.has(pathname)) return response;
    response.headers.set('Cross-Origin-Opener-Policy', 'same-origin');
    response.headers.set('Cross-Origin-Embedder-Policy', 'require-corp');
    response.headers.set('Cross-Origin-Resource-Policy', 'same-origin');
    return response;
  },
};
