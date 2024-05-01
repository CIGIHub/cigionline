import './css/policy_prompt.scss';
import 'mediaelement/src/css/mediaelementplayer.css';
import 'mediaelement/src/css/mejs-controls.svg';
import 'mediaelement/full';

const podcastChapters = document.getElementById('podcast-chapters');

$(document).ready(function () {
  // Add a class to the body to indicate that JS is enabled
  const podcastPlayer = $('#podcast-player').mediaelementplayer({
    alwaysShowControls: true,
    defaultAudioWidth: '100%',
    features: [
      'playpause',
      'current',
      'controls',
      'progress',
      'duration',
      'volume',
    ],
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
      const seconds = parseInt(timeArray[0], 10) * 3600
        + parseInt(timeArray[1], 10) * 60
        + parseInt(timeArray[2], 10);
      podcastPlayer[0].setCurrentTime(seconds);
      podcastPlayer[0].play();
    });
  });
});
