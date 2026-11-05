// =============================================================================
// Design System — Video facade
//
// Lightweight click-to-load video. [data-ds-video] shows a poster + play button;
// on play we swap in the provider iframe (autoplay). Avoids loading the heavy
// YouTube/Vimeo player until the user opts in (performance + privacy).
// =============================================================================

function toEmbedUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    const host = url.hostname.replace(/^www\./, '');

    if (host === 'youtu.be') {
      return `https://www.youtube.com/embed/${url.pathname.slice(1)}?autoplay=1`;
    }
    if (host.endsWith('youtube.com')) {
      const id = url.searchParams.get('v') || url.pathname.split('/').pop();
      return `https://www.youtube.com/embed/${id}?autoplay=1`;
    }
    if (host.endsWith('vimeo.com')) {
      const id = url.pathname.split('/').filter(Boolean).pop();
      return `https://player.vimeo.com/video/${id}?autoplay=1`;
    }
  } catch (err) {
    /* fall through to the raw URL */
  }
  return rawUrl;
}

function buildPlayer(container) {
  const fileUrl = container.dataset.dsVideoFile;
  const rawUrl = container.dataset.dsVideoUrl;

  // Uploaded file → native <video>; otherwise → provider iframe embed.
  if (fileUrl) {
    const video = document.createElement('video');
    video.className = 'ds-video__player';
    video.src = fileUrl;
    video.controls = true;
    video.autoplay = true;
    video.playsInline = true;
    return video;
  }
  if (rawUrl) {
    const iframe = document.createElement('iframe');
    iframe.className = 'ds-video__player';
    iframe.src = toEmbedUrl(rawUrl);
    iframe.title = container.dataset.dsVideoTitle || 'Video';
    iframe.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
    iframe.allowFullscreen = true;
    // The site-wide Referrer-Policy is same-origin, so a cross-origin embed
    // sends no referrer — YouTube rejects that with Error 153, "Video player
    // configuration error" (BugHerd #292). Match the oEmbed iframes' policy.
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    return iframe;
  }
  return null;
}

function playFacade(container) {
  if (container.dataset.dsPlaying) return;
  if (!(container.dataset.dsVideoFile || container.dataset.dsVideoUrl)) return;
  const player = buildPlayer(container);
  if (!player) return;
  container.dataset.dsPlaying = '1';
  container.innerHTML = '';
  container.appendChild(player);
}

// Event delegation (not per-element binding) so facades inside carousels keep
// working after Swiper clones their slides (loop mode) — clones inherit no
// listeners, but a delegated click on the root still resolves to them.
export default function initVideoFacades(root = document) {
  if (root.__dsVideoFacadeInit) return;
  root.__dsVideoFacadeInit = true;

  root.addEventListener('click', (event) => {
    const button = event.target.closest('[data-ds-video-play]');
    if (!button) return;
    const container = button.closest('[data-ds-video]');
    if (container) playFacade(container);
  });
}
