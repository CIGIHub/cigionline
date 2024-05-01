import './css/policy_prompt.scss';
import 'mediaelement/src/css/mediaelementplayer.css';
import 'mediaelement/src/css/mejs-controls.svg';
import 'mediaelement/full';

$(document).ready(function () {
  // Add a class to the body to indicate that JS is enabled
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

  const chapterTimes = document.querySelectorAll('.chapter-time');
  chapterTimes.forEach(function (chapterTime) {
    chapterTime.addEventListener('click', function (event) {
      event.preventDefault();
      const time = chapterTime.getAttribute('data-timestamp');
      // the time is in the format of hh:mm:ss. convert this time into seconds
      const timeArray = time.split(':');
      const seconds =
        parseInt(timeArray[0], 10) * 3600 +
        parseInt(timeArray[1], 10) * 60 +
        parseInt(timeArray[2], 10);
      podcastPlayer[0].setCurrentTime(seconds);
      podcastPlayer[0].play();
    });
  });
});

const text = ['prompt', 'policy'];
const speed = 125;
const textElement1 = document.getElementById('logo-animation-text-1');
const textElement2 = document.getElementById('logo-animation-text-2');

function typeText(word, element, index, callback) {
  if (index < word.length) {
    element.textContent += word[index];
    setTimeout(() => {
      typeText(word, element, index + 1, callback);
    }, speed);
  } else if (callback) {
    callback();
  }
}

function startTyping() {
  typeText(text[0], textElement1, 0, () => {
    textElement2.textContent = textElement1.textContent;
    textElement1.textContent = '';
    typeText(text[1], textElement1, 0, null);
  });

  setTimeout(() => {
    document.getElementById('logo-animation-cursor').classList.add('wobble');
  }, 2000);
}

// document.getElementById('test-animation').addEventListener('click', startTyping);
setTimeout(() => {
  startTyping();
}, 2000);
