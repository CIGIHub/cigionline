import './css/policy_prompt.scss';
import 'mediaelement/src/css/mediaelementplayer.css';
import 'mediaelement/src/css/mejs-controls.svg';
import 'mediaelement/full';

function typeText(text, elementId, speed, callback) {
  const line = document.getElementById(elementId);
  const textElement = line.children[0];
  let index = 0;

  function type() {
    if (index < text.length) {
      textElement.textContent += text.charAt(index);
      index += 1;
      setTimeout(type, speed);
    } else if (callback) {
      callback();
    }
  }

  type();
}

function startTyping(texts, speed) {
  document
    .getElementById('logo-animation-cursor-1')
    .classList.remove('offset-left');
  typeText(texts[0], 'line-1', speed, () => {
    document.getElementById('logo-animation-cursor-1').remove();
    document
      .getElementById('logo-animation-cursor-2')
      .classList.remove('hidden');

    setTimeout(() => {
      typeText(texts[1], 'line-2', speed, () => {
        document.getElementById('logo-animation-cursor-2').remove();
      });
    }, 250);
  });

  setTimeout(() => {
    const cursorEnd = document.getElementById('logo-animation-cursor-end');
    cursorEnd.classList.remove('hidden');
    cursorEnd.classList.add('wobble');
  }, 1250);
}

function getRandomIndices(total, count) {
  const indices = new Set();
  while (indices.size < count) {
    const randomIndex = Math.floor(Math.random() * total);
    indices.add(randomIndex);
  }
  return Array.from(indices);
}

function animateSpans(spans, totalSpans, batchSize) {
  spans.forEach((span) => span.classList.remove('animate-color'));

  const randomIndices = getRandomIndices(totalSpans, batchSize);

  randomIndices.forEach((index) => {
    spans[index].classList.add('animate-color');
  });
}

function startAnimationCycle(
  spans,
  totalSpans,
  batchSize,
  animationDuration,
  delayBetweenBatches,
) {
  animateSpans(spans, totalSpans, batchSize);
  setInterval(() => {
    animateSpans(spans, totalSpans, batchSize);
  }, animationDuration + delayBetweenBatches);
}

function scrollToElement(e) {
  e.preventDefault();

  const OFFSET = 80;
  const targetId = this.getAttribute('href').substring(1);
  const targetElement = document.getElementById(targetId);
  const targetPosition = targetElement.getBoundingClientRect().top + window.scrollY - OFFSET;

  window.scrollTo({
    top: targetPosition,
    behavior: 'smooth',
  });
}

$(document).ready(function () {
  const podcastPlayer = $('#podcast-player').mediaelementplayer({
    alwaysShowControls: true,
    defaultAudioWidth: '100%',
    features: [
      'playpause',
      'current',
      'progress',
      'duration',
      'tracks',
      'volume',
    ],
    success(media, node, player) {
      const buildRewindButton = function () {
        const button = document.createElement('button');
        button.className = 'mejs__button mejs__rewind-button';
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-rotate-left';
        button.appendChild(icon);
        button.addEventListener('click', function () {
          media.setCurrentTime(Math.max(media.getCurrentTime() - 15, 0));
        });
        return button;
      };

      const buildFastForwardButton = function () {
        const button = document.createElement('button');
        button.className = 'mejs__button mejs__fast-forward-button';
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-rotate-right';
        button.appendChild(icon);
        button.addEventListener('click', function () {
          media.setCurrentTime(
            Math.min(media.getCurrentTime() + 15, media.duration),
          );
        });
        return button;
      };

      const controls = player.controls;
      const playpause = controls.childNodes[0];
      controls.insertBefore(buildRewindButton(), playpause);
      controls.insertBefore(buildFastForwardButton(), playpause.nextSibling);
    },
  });

  const svgUses = document.querySelectorAll('svg[class*="mejs__icon-"] > use');
  svgUses.forEach(function (use) {
    const currentHref = use.getAttribute('xlink:href');
    use.setAttribute('xlink:href', `/static/assets/${currentHref}`);
  });

  function navigateToChapter(chapter) {
    const time = chapter.getAttribute('data-timestamp');
    const timeArray = time.split(':');
    const seconds =
      parseInt(timeArray[0], 10) * 60 + parseInt(timeArray[1], 10);
    podcastPlayer[0].setCurrentTime(seconds);
    podcastPlayer[0].play();
  }

  const chapterTimes = document.querySelectorAll('.chapter-time');
  if (chapterTimes.length) {
    chapterTimes.forEach(function (chapterTime) {
      chapterTime.addEventListener('click', function (event) {
        event.preventDefault();
        navigateToChapter(chapterTime);
      });
    });
  }

  const transcriptTimes = document.querySelectorAll('.transcript-text');
  if (transcriptTimes.length) {
    transcriptTimes.forEach(function (transcriptTime) {
      transcriptTime.addEventListener('click', function (event) {
        event.preventDefault();
        navigateToChapter(transcriptTime);
      });
    });
  }

  if (document.getElementsByClassName('policy-prompt-multimedia').length) {
    const spans = document.querySelectorAll('#animated-title span');
    const totalSpans = spans.length;
    const batchSize = 5;
    const animationDuration = 6000;
    const delayBetweenBatches = 0;

    startAnimationCycle(
      spans,
      totalSpans,
      batchSize,
      animationDuration,
      delayBetweenBatches,
    );

    const scrollLinks = document.querySelectorAll('.scroll-link');
    scrollLinks.forEach((link) => {
      link.addEventListener('click', scrollToElement);
    });
  }

  if (
    document.getElementsByClassName('policy-prompt-multimedia-series').length
  ) {
    const texts = ['policy', 'prompt'];
    const speed = 75;
    setTimeout(() => {
      startTyping(texts, speed);
    }, 2000);
  }
});
