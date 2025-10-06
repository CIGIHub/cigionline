import './css/article_page.scss';

document.addEventListener('DOMContentLoaded', () => {
  const player = document.getElementById('ttsPlayer');
  if (!player) return;

  const audio = document.getElementById(player.getAttribute('data-target') || '');
  if (!audio) return;

  const fab = player.querySelector('.tts-fab');
  const progress = player.querySelector('.tts-progress');
  const bar       = player.querySelector('.tts-bar');
  const timeEl = document.getElementById('ttsTime');
  const promptEl = document.getElementById('ttsPrompt');
  const sentinel  = document.getElementById('ttsSentinel');
  const closeBtn  = player.querySelector('.tts-close'); // ⬅️ now from template

  // Session flags
  let hasInteracted = false;      // true after first play this session
  let sentinelOutOfView = false;  // true when we've scrolled past the sentinel
  let stickyDismissed = false;

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
      timeEl.textContent = (isFinite(dur) && dur > 0) ? fmt(dur) : '00:00';
    } else {
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

  // Sticky only when: scrolled past sentinel AND user has interacted AND not dismissed
  const updateSticky = () => {
    const shouldStick = Boolean(sentinelOutOfView && hasInteracted && !stickyDismissed);
    player.classList.toggle('is-sticky', shouldStick);
    // No direct style toggling; CSS shows .tts-close when .is-sticky is present
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
      stickyDismissed = false;
      audio.play().then(() => {
        hasInteracted = true;
        flipToProgress();
        setPlayingState(true);
        updateSticky();
      }).catch(() => {});
    } else {
      audio.pause(); // pause does NOT close sticky
    }
  });

  // Close button: pause if playing, then dismiss sticky for this session
  closeBtn && closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    stickyDismissed = true;
    if (!audio.paused) audio.pause();
    updateSticky(); // hides sticky (and the close button via CSS)
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
    stickyDismissed = false;
    hasInteracted = true;
    flipToProgress();
    setPlayingState(true);
    updateSticky();
  });

  audio.addEventListener('pause', () => {
    setPlayingState(false);
    // keep sticky open after pause (user closes via X)
    updateSticky();
  });

  audio.addEventListener('ended', () => {
    setPlayingState(false);
    // keep sticky open after end
    updateSticky();
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
    let sentTop = sentinel.getBoundingClientRect().top + window.pageYOffset;
    const recalc = () => { sentTop = sentinel.getBoundingClientRect().top + window.pageYOffset; };
    window.addEventListener('resize', () => { recalc(); setLineWidth(); updateSticky(); }, { passive: true });
    window.addEventListener('scroll', () => {
      sentinelOutOfView = window.pageYOffset > sentTop;
      updateSticky();
    }, { passive: true });
  }

  // Pause if navigating away (optional)
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
