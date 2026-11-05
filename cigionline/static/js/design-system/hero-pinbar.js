// =============================================================================
// Design System — Event hero pin-bar (BugHerd #202)
//
// The event hero carries a condensed title · date · location bar
// ([data-ds-hero-pinbar], rendered in content_hero.html). Once the hero scrolls
// out of view, the bar fixes below the pinned header row; scrolling back up
// hides it again. Markup lives in the template — this only observes and toggles.
// Without JS the bar never shows (it starts translated away and inert).
// =============================================================================

const VISIBLE = 'ds-hero__pinbar--visible';
const PLAYING = 'ds-hero__pinbar-play--playing';

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// Compact TTS dock (BugHerd #298): the pinbar's play button drives the hero's
// one <audio data-ds-audio> (Plyr-enhanced) — never a second player.
function wirePinbarAudio(bar, hero) {
  const button = bar.querySelector('[data-ds-pinbar-play]');
  const time = bar.querySelector('[data-ds-pinbar-time]');
  const audio = hero.querySelector('audio[data-ds-audio]');
  if (!button || !audio) return;

  button.addEventListener('click', () => {
    if (audio.paused) audio.play();
    else audio.pause();
  });
  const syncPressed = () => {
    button.setAttribute('aria-pressed', String(!audio.paused));
    button.classList.toggle(PLAYING, !audio.paused);
  };
  audio.addEventListener('play', syncPressed);
  audio.addEventListener('pause', syncPressed);
  if (time) {
    audio.addEventListener('timeupdate', () => {
      time.textContent = formatTime(audio.currentTime);
    });
  }
}

export default function initHeroPinbars(root = document) {
  root.querySelectorAll('[data-ds-hero-pinbar]').forEach((bar) => {
    if (bar.dataset.dsInit) return;
    bar.dataset.dsInit = '1';

    const hero = bar.closest('.ds-hero');
    if (!hero || !('IntersectionObserver' in window)) return;

    wirePinbarAudio(bar, hero);

    // Trigger on the TITLE, not the whole hero — event heroes are tall (banner
    // + excerpt + Register), so waiting for the full hero to pass fired far too
    // late. The bar appears the moment the title slides under the pinned header
    // row, which is when the reader loses sight of what page they are on.
    const target = hero.querySelector('.ds-hero__title') || hero;
    const offset = parseFloat(
      window.getComputedStyle(document.documentElement)
        .getPropertyValue('--ds-header-pinned-height'),
    ) || 0;

    const observer = new window.IntersectionObserver(([entry]) => {
      const passed = !entry.isIntersecting && entry.boundingClientRect.bottom < offset;
      bar.classList.toggle(VISIBLE, passed);
    }, { rootMargin: `-${offset}px 0px 0px 0px` });
    observer.observe(target);
  });
}
