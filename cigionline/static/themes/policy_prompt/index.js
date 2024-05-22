import './css/policy_prompt.scss';
import 'mediaelement/src/css/mediaelementplayer.css';
import 'mediaelement/src/css/mejs-controls.svg';
import 'mediaelement/full';

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
      parseInt(timeArray[0], 10) * 60 +
      parseInt(timeArray[1], 10);
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
});

const texts = ['policy', 'prompt'];
const speed = 75;

function typeText(text, elementId, callback) {
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

function startTyping() {
  document.getElementById('logo-animation-cursor-1').classList.remove('offset-left');
  typeText(texts[0], 'line-1', () => {
    document.getElementById('logo-animation-cursor-1').remove();
    document
      .getElementById('logo-animation-cursor-2')
      .classList.remove('hidden');

    setTimeout(() => {
      typeText(texts[1], 'line-2', () => {
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

if (document.getElementsByClassName('policy-prompt-multimedia-series').length) {
  setTimeout(() => {
    startTyping();
  }, 2000);
}
