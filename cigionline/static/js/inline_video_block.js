export default function addInlineVideoActions() {
  $(function () {
    $('.stream-block-inline-video').each(function () {
      const watchLabel = $(this).find('.watch-video-label');
      const imageWrapper = $(this).find('.img-wrapper');
      const videoWrapper = $(this).find('.video-wrapper');
      const closeVideo = $(this).find('.close-video-icon');
      const iframe = videoWrapper.find('iframe');

      iframe[0].src += '&enablejsapi=1&autoplay=0';

      function toggleElements(action) {
        let closingElement;
        let openingElement;

        if (action === 'stop') {
          closingElement = videoWrapper;
          openingElement = imageWrapper;
          iframe[0].contentWindow.postMessage('{"event":"command","func":"stopVideo","args":""}', '*');
        } else if (action === 'play') {
          closingElement = imageWrapper;
          openingElement = videoWrapper;
        }

        watchLabel.toggleClass('shrink');
        closeVideo.toggleClass('hidden');
        closingElement.toggleClass('shrink');
        setTimeout(function() {
          openingElement.toggleClass('shrink');
          if (action === 'play') {
            setTimeout(function() {
              iframe[0].src = iframe[0].src.replace('autoplay=0', 'autoplay=1');
            }, 1500);
          }
        }, 1500);
      }

      imageWrapper.on('click', function() {
        toggleElements('play');
      });
      watchLabel.on('click', function() {
        toggleElements('play');
      });
      closeVideo.on('click', function() {
        toggleElements('stop');
      });
    });
  });
}
