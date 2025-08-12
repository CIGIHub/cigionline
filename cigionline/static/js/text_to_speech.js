/* Text-to-Speech (TTS) for Wagtail (data-attribute auto-init)
   - Add data-tts to any container to get controls & read text inside it.
   - Optional attributes on the container:
       data-tts-selectors="h1,h2,p,li"   // override default text selectors
       data-tts-position="before|after|inside-start|inside-end" // default: before
       data-tts-lang="en"                 // prefer voices matching this BCP-47 code
   - To skip a subtree from reading, add data-tts-skip on that element.
*/
(function () {
  if (!('speechSynthesis' in window)) {
    console.warn('TTS: speechSynthesis not supported');
    return;
  }

  const DEFAULT_SELECTORS = [
    'h1,h2,h3,h4,h5,h6',
    'p',
    'li',
    'blockquote',
    'figcaption',
    '.rich-text p, .richtext p',
    '.prose p',
  ].join(',');

  function placeControls(controls, target, position) {
    switch (position) {
      case 'after': target.insertAdjacentElement('afterend', controls); break;
      case 'inside-start': target.insertAdjacentElement('afterbegin', controls); break;
      case 'inside-end': target.insertAdjacentElement('beforeend', controls); break;
      case 'before':
      default: target.insertAdjacentElement('beforebegin', controls);
    }
  }

  function buildControls() {
    const wrap = document.createElement('div');
    wrap.className = 'tts-controls';
    wrap.style.cssText = 'margin:1rem 0;display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;';
    wrap.innerHTML = `
      <button type="button" class="tts-play" aria-label="Play text to speech">🔊 Listen</button>
      <button type="button" class="tts-pause" aria-label="Pause">⏸️ Pause</button>
      <button type="button" class="tts-resume" aria-label="Resume">🔄 Resume</button>
      <button type="button" class="tts-stop" aria-label="Stop">⏹️ Stop</button>
      <label style="margin-left:.75rem">Rate <input class="tts-rate" type="range" min="0.6" max="1.8" step="0.1" value="1"></label>
      <label>Pitch <input class="tts-pitch" type="range" min="0" max="2" step="0.1" value="1"></label>
    `;
    return wrap;
  }

  function collectChunks(root, selectors) {
    const nodes = Array.from(root.querySelectorAll(selectors)).filter(el => {
      // skip anything inside a data-tts-skip subtree
      if (el.closest('[data-tts-skip]')) return false;
      const style = window.getComputedStyle(el);
      const ariaHidden = el.closest('[aria-hidden="true"], [hidden]');
      return style.display !== 'none' && style.visibility !== 'hidden' && !ariaHidden && el.innerText.trim().length;
    });

    const chunks = [];
    const SENTENCE_SPLIT = /(?<=[.?!。！？])\s+(?=[A-Z0-9“"‘'(\[])/;

    for (const el of nodes) {
      const text = el.innerText.replace(/\s+/g, ' ').trim();
      if (!text) continue;
      if (text.length > 280) {
        text.split(SENTENCE_SPLIT).forEach(s => s && chunks.push(s.trim()));
      } else {
        chunks.push(text);
      }
    }
    return chunks;
  }

  function initTTSForElement(container) {
    const selectors = container.getAttribute('data-tts-selectors') || DEFAULT_SELECTORS;
    const position = (container.getAttribute('data-tts-position') || 'before').toLowerCase();
    const preferredLang =
      container.getAttribute('data-tts-lang') ||
      document.documentElement.lang ||
      '';

    const controls = buildControls();
    placeControls(controls, container, position);

    const synth = window.speechSynthesis;
    const rateEl = controls.querySelector('.tts-rate');
    const pitchEl = controls.querySelector('.tts-pitch');

    const playBtn = controls.querySelector('.tts-play');
    const pauseBtn = controls.querySelector('.tts-pause');
    const resumeBtn = controls.querySelector('.tts-resume');
    const stopBtn = controls.querySelector('.tts-stop');

    let queue = [];
    let current = null;

    function pickVoice() {
      const voices = synth.getVoices();
      return (
        (preferredLang && voices.find(v => v.lang.toLowerCase().startsWith(preferredLang.toLowerCase()))) ||
        voices.find(v => v.lang.startsWith('en')) ||
        voices[0] || null
      );
    }

    function speakNext() {
      if (!queue.length) { current = null; return; }
      const text = queue.shift();
      const u = new SpeechSynthesisUtterance(text);
      u.rate = parseFloat(rateEl.value || '1');
      u.pitch = parseFloat(pitchEl.value || '1');
      const voice = pickVoice();
      if (voice) u.voice = voice;
      u.onend = () => { current = null; speakNext(); };
      u.onerror = (e) => { console.error('TTS error', e); current = null; speakNext(); };
      current = u;
      synth.speak(u);
    }

    function start() {
      synth.cancel();
      queue = collectChunks(container, selectors);
      if (!queue.length) return;
      speakNext();
    }

    playBtn.addEventListener('click', start);
    pauseBtn.addEventListener('click', () => { if (synth.speaking && !synth.paused) synth.pause(); });
    resumeBtn.addEventListener('click', () => { if (synth.paused) synth.resume(); });
    stopBtn.addEventListener('click', () => { queue = []; synth.cancel(); current = null; });

    // Ensure voices list is ready on browsers that load them async
    if (typeof speechSynthesis.onvoiceschanged !== 'undefined') {
      speechSynthesis.onvoiceschanged = () => {};
    }
  }

  // Auto-init on any element with data-tts
  function autoInit() {
    document.querySelectorAll('[data-tts]').forEach(initTTSForElement);
  }

  // Public API in case you want to target dynamically-added content
  window.initTTS = function (selectorOrElement) {
    if (!selectorOrElement) return;
    if (typeof selectorOrElement === 'string') {
      document.querySelectorAll(selectorOrElement).forEach(initTTSForElement);
    } else {
      initTTSForElement(selectorOrElement);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }
})();
