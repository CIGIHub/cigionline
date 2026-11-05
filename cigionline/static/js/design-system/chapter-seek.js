// =============================================================================
// Design System — Podcast chapter seek (BugHerd #305)
//
// Chapter rows (podcast_reading_tail.html) render a `.chapter-time` link with a
// `data-timestamp` ("0:27:03"). Clicking one seeks the page's audio player (the
// hero's Plyr-enhanced <audio data-ds-audio>) to that time and plays. The
// anchor's own fragment jump is kept. Delegated, so it needs no per-row wiring.
// =============================================================================

function toSeconds(timestamp) {
  const parts = timestamp.trim().split(':').map(Number);
  if (!parts.length || parts.some(Number.isNaN)) return null;
  return parts.reduce((total, part) => total * 60 + part, 0);
}

export default function initChapterSeek(root = document) {
  if (root.__dsChapterSeekInit) return;
  root.__dsChapterSeekInit = true;

  root.addEventListener('click', (event) => {
    const link = event.target.closest('.chapter-time[data-timestamp]');
    if (!link) return;
    const audio = document.querySelector('audio[data-ds-audio]');
    if (!audio) return;
    const seconds = toSeconds(link.dataset.timestamp);
    if (seconds === null) return;

    const seek = () => {
      audio.currentTime = seconds;
      audio.play();
    };
    // Before any interaction the source metadata may not be loaded yet —
    // currentTime would be dropped. Wait for it once, then seek.
    if (audio.readyState >= 1) {
      seek();
    } else {
      audio.addEventListener('loadedmetadata', seek, { once: true });
      audio.load();
    }
  });
}
