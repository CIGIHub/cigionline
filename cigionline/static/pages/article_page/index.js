import './css/article_page.scss';

document.addEventListener('DOMContentLoaded', () => {
  const player = document.getElementById('ttsPlayer');
  if (!player) return;

  const audio = document.getElementById(player.getAttribute('data-target') || '');
  if (!audio) return;

  const fab = player.querySelector('.tts-fab');
  const progress = player.querySelector('.tts-progress');
  const bar      = player.querySelector('.tts-bar');
  const timeEl = document.getElementById('ttsTime');
  const promptEl = document.getElementById('ttsPrompt');
  const sentinel = document.getElementById('ttsSentinel');

  // Session flags for sticky behavior
  let hasInteracted = false;     // becomes true after first play this session
  let sentinelOutOfView = false; // true when we've scrolled past the sentinel

  const fmt = (t) => {
    if (!isFinite(t)) return '00:00';
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60);
    return (m < 10 ? '0' + m : String(m)) + ':' + (s < 10 ? '0' + s : String(s));
  };

  const updateTime = () => {
    const cur = audio.currentTime || 0;
    const dur = audio.duration || 0;

    if (!timeEl) return;

    if (!hasInteracted) {
      // Before first play: show only total length
      timeEl.textContent = (isFinite(dur) && dur > 0) ? fmt(dur) : '00:00';
    } else {
      // After first play: show current / total
      const total = (isFinite(dur) && dur > 0) ? ' / ' + fmt(dur) : '';
      timeEl.textContent = fmt(cur) + total;
    }
  };

  const updateProgress = () => {
    const dur = audio.duration || 0;
    const cur = audio.currentTime || 0;
    const pct = dur ? (cur / dur) * 100 : 0;
    if (bar) bar.style.width = pct + '%';
    if (progress) progress.setAttribute('aria-valuenow', String(Math.round(pct)));
  };

  const setPlayingState = (isPlaying) => {
    player.classList.toggle('is-playing', isPlaying);
    if (fab) {
      fab.setAttribute('aria-pressed', isPlaying ? 'true' : 'false');
      fab.setAttribute('aria-label', isPlaying ? 'Pause article audio' : 'Play article audio');
    }
  };

  // Show progress (and hide prompt) after the first play
  const flipToProgress = () => {
    if (!player.classList.contains('has-started')) {
      player.classList.add('has-started');
      if (promptEl) promptEl.setAttribute('aria-hidden', 'true');
      if (progress) progress.setAttribute('aria-hidden', 'false');
    }
  };

  // Sticky only when: scrolled past sentinel AND user has interacted AND audio is playing
  const updateSticky = () => {
    const shouldStick = Boolean(sentinelOutOfView && hasInteracted && !audio.paused);
    player.classList.toggle('is-sticky', shouldStick);
  };

  // Measure prompt width so progress matches it exactly
  const setLineWidth = () => {
    if (!promptEl) return;
    const style = getComputedStyle(promptEl);
    const wasHidden = style.display === 'none' || style.visibility === 'hidden';
    if (wasHidden) promptEl.style.display = '';
    const w = Math.ceil(promptEl.getBoundingClientRect().width);
    player.style.setProperty('--tts-line', w > 0 ? `${w}px` : '12ch');
    if (wasHidden) promptEl.style.display = 'none';
  };

  // Play/pause toggle (no reset)
  fab && fab.addEventListener('click', () => {
    if (audio.paused) {
      audio.play().then(() => {
        hasInteracted = true;
        flipToProgress();
        setPlayingState(true);
        updateSticky();
      }).catch(() => {});
    } else {
      audio.pause(); // pause event will clear sticky
    }
  });

  // Click-to-seek on progress track
  progress && progress.addEventListener('click', (e) => {
    const rect = progress.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, x / rect.width));
    if (isFinite(audio.duration) && audio.duration > 0) {
      audio.currentTime = audio.duration * pct;
    }
  });

  // Audio events
  audio.addEventListener('play', () => {
    hasInteracted = true;
    flipToProgress();
    setPlayingState(true);
    updateSticky();
  });

  audio.addEventListener('pause', () => {
    setPlayingState(false);
    player.classList.remove('is-sticky'); // hide sticky when paused
  });

  audio.addEventListener('ended', () => {
    setPlayingState(false);
    player.classList.remove('is-sticky'); // also hide on end
  });

  audio.addEventListener('timeupdate', () => { updateTime(); updateProgress(); });
  audio.addEventListener('loadedmetadata', () => { updateTime(); updateProgress(); });

  // Sticky behavior with IntersectionObserver
  if ('IntersectionObserver' in window && sentinel) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        sentinelOutOfView = entry.intersectionRatio === 0;
        updateSticky();
      });
    }, { rootMargin: '0px', threshold: [0] });
    io.observe(sentinel);
  } else if (sentinel) {
    // Fallback scroll/resize
    let sentTop = sentinel.getBoundingClientRect().top + window.pageYOffset;
    const recalc = () => { sentTop = sentinel.getBoundingClientRect().top + window.pageYOffset; };
    window.addEventListener('resize', () => { recalc(); setLineWidth(); updateSticky(); }, { passive: true });
    window.addEventListener('scroll', () => {
      sentinelOutOfView = window.pageYOffset > sentTop;
      updateSticky();
    }, { passive: true });
  }

  // Pause if navigating away (optional nicety)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && !audio.paused) audio.pause();
  });

  // If page loads with a non-zero currentTime, show progress immediately
  if ((audio.currentTime || 0) > 0) {
    hasInteracted = true;
    flipToProgress();
  }

  // Initial layout
  setLineWidth();
  updateTime();
  updateProgress();

  // Keep line width in sync with viewport changes
  window.addEventListener('resize', setLineWidth, { passive: true });
});
