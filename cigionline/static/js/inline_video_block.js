export default function addInlineVideoActions() {
  $(function () {
    $('.stream-block-inline-video').each(function () {
      const watchLabel = $(this).find('.watch-video-label');
      const imageWrapper = $(this).find('.img-wrapper');
      const videoWrapper = $(this).find('.video-wrapper');
      const closeVideo = $(this).find('.close-video-icon');
      const iframe = videoWrapper.find('iframe');

      iframe[0].allow += 'autoplay';
      iframe[0].src += '&enablejsapi=1';

      
      function toggleElements(elementOne, elementTwo) {
        watchLabel.toggleClass('shrink');
        closeVideo.toggleClass('hidden');
        elementOne.toggleClass('shrink');
        setTimeout(function() {
          elementTwo.toggleClass('shrink');
        }, 2000);
      }


      watchLabel.on('click', function() {
        toggleElements(imageWrapper, videoWrapper);
      });
      closeVideo.on('click', function() {
        toggleElements(videoWrapper, imageWrapper);
      });
    });
  });
}
