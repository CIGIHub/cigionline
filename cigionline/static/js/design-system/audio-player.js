// =============================================================================
// Design System — Audio player
//
// A native <audio data-ds-audio> enhanced by Plyr. The custom controls markup
// (and its SVGs) lives in the includes/audio_player.html <template> — read here
// and handed to Plyr — so no markup/SVG lives in this file. Plyr drives
// playback, seeking and time; we only wire it.
//
// First principles: no hand-rolled engine; native `controls` is the no-JS
// fallback; idempotent init (safe after router swaps).
// =============================================================================
import Plyr from 'plyr';
import 'plyr/dist/plyr.css';

export default function initAudioPlayers(root = document) {
  root.querySelectorAll('audio[data-ds-audio]').forEach((el) => {
    if (el.dataset.dsAudioReady) return;
    el.dataset.dsAudioReady = 'true';
    const wrap = el.closest('.ds-audio');
    const template = wrap && wrap.querySelector('[data-ds-audio-controls]');
    el.plyr = new Plyr(el, {
      controls: template ? template.innerHTML : undefined,
      settings: ['speed'],
      speed: { selected: 1, options: [0.75, 1, 1.25, 1.5] },
      seekTime: 10,
      loadSprite: false,
    });

    // Speed control (BugHerd #298): the custom controls carry a cycle button
    // ([data-ds-audio-speed], markup in audio_player.html) instead of Plyr's
    // settings menu — one tap per step: 1 → 1.25 → 1.5 → 0.75.
    const SPEEDS = [1, 1.25, 1.5, 0.75];
    el.plyr.on('ready', () => {
      const speedButton = wrap && wrap.querySelector('[data-ds-audio-speed]');
      const label = speedButton && speedButton.querySelector('[data-ds-audio-speed-label]');
      if (!speedButton || !label) return;
      // Tracked locally — Plyr's speed accessor is unreliable mid-cycle; the
      // media element's playbackRate is the effect and Plyr syncs from its
      // ratechange event.
      let speedIndex = 0;
      speedButton.addEventListener('click', () => {
        speedIndex = (speedIndex + 1) % SPEEDS.length;
        el.playbackRate = SPEEDS[speedIndex];
        label.textContent = `${SPEEDS[speedIndex]}×`;
      });
    });
  });
}
