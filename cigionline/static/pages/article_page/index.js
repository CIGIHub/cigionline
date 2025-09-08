import './css/article_page.scss';

document.addEventListener('DOMContentLoaded', () => {
  const player = document.getElementById('ttsPlayer');
  if (!player) return;

  const audioId = player.getAttribute('data-target');
  const audio = document.getElementById(audioId);
  if (!audio) return;

  const fab = player.querySelector('.tts-fab');
  const bar = player.querySelector('.tts-bar');
  const timeEl = document.getElementById('ttsTime');
  const progress = player.querySelector('.tts-progress');
  const sentinel = document.getElementById('ttsSentinel');

  const fmt = t => {
    if (!isFinite(t)) return '00:00';
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60);
    return (m < 10 ? '0' + m : String(m)) + ':' + (s < 10 ? '0' + s : String(s));
  };

  const updateTime = () => {
    const cur = audio.currentTime || 0;
    const dur = audio.duration || 0;
    timeEl.textContent = fmt(cur) + (isFinite(dur) && dur > 0 ? ' / ' + fmt(dur) : '');
  };

  const updateProgress = () => {
    const dur = audio.duration || 0;
    const cur = audio.currentTime || 0;
    const pct = dur ? (cur / dur) * 100 : 0;
    bar.style.width = pct + '%';
    progress.setAttribute('aria-valuenow', String(Math.round(pct)));
  };

  const setPlayingState = isPlaying => {
    player.classList.toggle('is-playing', isPlaying);
    fab.setAttribute('aria-pressed', isPlaying ? 'true' : 'false');
    fab.setAttribute('aria-label', isPlaying ? 'Pause article audio' : 'Play article audio');
  };

  // Play/pause toggle (no stop/reset)
  fab.addEventListener('click', () => {
    if (audio.paused) {
      audio.play().catch(() => {});
    } else {
      audio.pause();
    }
  });

  // Keyboard activation is native for <button>, no extra handler needed.
  // Click-to-seek
  progress.addEventListener('click', e => {
    const rect = progress.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = x / rect.width;
    if (isFinite(audio.duration)) {
      audio.currentTime = Math.max(0, Math.min(audio.duration * pct, audio.duration));
    }
  });

  // Audio events
  audio.addEventListener('play', () => setPlayingState(true));
  audio.addEventListener('pause', () => setPlayingState(false));
  audio.addEventListener('ended', () => setPlayingState(false));
  audio.addEventListener('timeupdate', () => { updateTime(); updateProgress(); });
  audio.addEventListener('loadedmetadata', () => { updateTime(); updateProgress(); });

  // Sticky on scroll using IntersectionObserver
  if ('IntersectionObserver' in window && sentinel) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        player.classList.toggle('is-sticky', entry.intersectionRatio === 0);
      });
    }, { rootMargin: '0px', threshold: [0] });
    io.observe(sentinel);
  } else if (sentinel) {
    let sentTop = sentinel.getBoundingClientRect().top + window.pageYOffset;
    const recalc = () => { sentTop = sentinel.getBoundingClientRect().top + window.pageYOffset; };
    window.addEventListener('resize', recalc, { passive: true });
    window.addEventListener('scroll', () => {
      const stuck = window.pageYOffset > sentTop;
      player.classList.toggle('is-sticky', stuck);
    }, { passive: true });
  }

  // Pause if navigating away (optional)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && !audio.paused) audio.pause();
  });
});
