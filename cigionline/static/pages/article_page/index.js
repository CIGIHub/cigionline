import './css/article_page.scss';

document.addEventListener('DOMContentLoaded', () => {
  const player = document.getElementById('ttsPlayer');
  if (!player) return;

  const audio = document.getElementById(player.getAttribute('data-target') || '');
  if (!audio) return;

  const fab = player.querySelector('.tts-fab');
  const progress = player.querySelector('.tts-progress');
  const bar = player.querySelector('.tts-bar');
  const timeEl = document.getElementById('ttsTime');
  const promptEl = document.getElementById('ttsPrompt');
  const sentinel = document.getElementById('ttsSentinel');
  const closeBtn = player.querySelector('.tts-close');

  // speed UI elements
  const speedBtn = player.querySelector('.tts-speed-btn');
  const speedMenu = player.querySelector('.tts-speed-menu');
  const speedOptions = player.querySelectorAll('.tts-speed-option');

  const speedRateNum = speedBtn ? speedBtn.querySelector('.rate-num') : null;

  // Session flags
  let hasInteracted = false;
  let sentinelOutOfView = false;
  let stickyDismissed = false;

  // playback speed config + persistence
  const speedSteps = [0.75, 1, 1.25, 1.5];
  const speedStorageKey = 'ttsPlaybackRate';

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

  const flipToProgress = () => {
    if (!player.classList.contains('has-started')) {
      player.classList.add('has-started');
      if (promptEl) promptEl.setAttribute('aria-hidden', 'true');
      if (progress) progress.setAttribute('aria-hidden', 'false');
    }
  };

  const updateSticky = () => {
    const shouldStick = Boolean(sentinelOutOfView && hasInteracted && !stickyDismissed);
    player.classList.toggle('is-sticky', shouldStick);
  };

  const setLineWidth = () => {
    if (!promptEl) return;
    const style = getComputedStyle(promptEl);
    const wasHidden = style.display === 'none' || style.visibility === 'hidden';
    if (wasHidden) promptEl.style.display = '';
    const w = Math.ceil(promptEl.getBoundingClientRect().width);
    player.style.setProperty('--tts-line', w > 0 ? `${w}px` : '12ch');
    if (wasHidden) promptEl.style.display = 'none';
  };

  // speed helpers
  // CHANGED: keep for aria-label only; do NOT write it into button text.
  const formatRate = (rate) => String(Number(rate)) + '×';

  const applyRate = (rate) => {
    const numericRate = Number(rate);
    if (!isFinite(numericRate) || numericRate <= 0) return;
    if (!speedSteps.includes(numericRate)) return;

    audio.playbackRate = numericRate;

    // CHANGED: do NOT overwrite speedBtn textContent (it nukes child spans and CSS hook)
    // Update the number span only; CSS appends the × via ::after
    if (speedRateNum) {
      speedRateNum.textContent = String(numericRate);
    }

    if (speedBtn) {
      speedBtn.setAttribute('aria-label', `Playback speed ${formatRate(numericRate)}`);
    }

    if (speedOptions && speedOptions.length) {
      speedOptions.forEach((optionButton) => {
        const optionRate = Number(optionButton.getAttribute('data-rate'));
        const isSelected = optionRate === numericRate;
        optionButton.classList.toggle('is-selected', isSelected);
        optionButton.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      });
    }
  };

  const getInitialRate = () => 1;

  const openSpeedMenu = () => {
    if (!speedBtn || !speedMenu) return;
    speedBtn.setAttribute('aria-expanded', 'true');
    speedMenu.setAttribute('aria-hidden', 'false');
    player.classList.add('speed-open');
  };

  const closeSpeedMenu = () => {
    if (!speedBtn || !speedMenu) return;
    speedBtn.setAttribute('aria-expanded', 'false');
    speedMenu.setAttribute('aria-hidden', 'true');
    player.classList.remove('speed-open');
  };

  const toggleSpeedMenu = () => {
    const expanded = speedBtn && speedBtn.getAttribute('aria-expanded') === 'true';
    if (expanded) closeSpeedMenu();
    else openSpeedMenu();
  };

  // speed button click opens/closes menu
  speedBtn && speedBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleSpeedMenu();
  });

  // speed option click selects speed and closes
  speedOptions && speedOptions.forEach((optionButton) => {
    optionButton.addEventListener('click', (e) => {
      e.stopPropagation();
      const nextRate = optionButton.getAttribute('data-rate');
      applyRate(nextRate);

      try {
        window.localStorage.setItem(speedStorageKey, String(Number(nextRate)));
      } catch (error) {}

      closeSpeedMenu();
    });
  });

  // close menu on outside click
  document.addEventListener('click', (e) => {
    if (!speedMenu || !speedBtn) return;
    const clickedInside = player.contains(e.target);
    if (!clickedInside) closeSpeedMenu();
  });

  // close menu on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSpeedMenu();
  });

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
      audio.pause();
    }
  });

  closeBtn && closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    stickyDismissed = true;
    if (!audio.paused) audio.pause();
    updateSticky();
  });

  progress && progress.addEventListener('click', (e) => {
    const rect = progress.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, x / rect.width));
    if (isFinite(audio.duration) && audio.duration > 0) {
      audio.currentTime = audio.duration * pct;
    }
  });

  audio.addEventListener('play', () => {
    stickyDismissed = false;
    hasInteracted = true;
    flipToProgress();
    setPlayingState(true);
    updateSticky();
  });

  audio.addEventListener('pause', () => {
    setPlayingState(false);
    updateSticky();
  });

  audio.addEventListener('ended', () => {
    setPlayingState(false);
    updateSticky();
  });

  audio.addEventListener('timeupdate', () => { updateTime(); updateProgress(); });
  audio.addEventListener('loadedmetadata', () => { updateTime(); updateProgress(); });

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

  // If page loads with a non-zero currentTime, show progress immediately
  if ((audio.currentTime || 0) > 0) {
    hasInteracted = true;
    flipToProgress();
  }

  // Initial layout
  setLineWidth();

  // apply saved/default speed on init + mark selected option
  applyRate(getInitialRate());

  updateTime();
  updateProgress();

  window.addEventListener('resize', setLineWidth, { passive: true });
});
