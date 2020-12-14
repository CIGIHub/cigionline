export default function addInlineVideoActions() {
  const inlineVideoBlocks = document.getElementsByClassName('stream-block-inline-video');

  for (const block of inlineVideoBlocks) {
    const watchLabel = block.getElementsByClassName('stream-block-inline-video-label')[0];
    const blockImage = block.getElementsByClassName('img-wrapper')[0];
    const blockVideo = block.getElementsByClassName('video-wrapper')[0];
    watchLabel.addEventListener('click', function () {
      if (blockImage.classList.contains('shrink')) {
        blockVideo.classList.add('shrink');
        window.setTimeout(function() {
          blockImage.classList.remove('shrink');
        }, 1000)
      } else {
        blockImage.classList.add('shrink');
        window.setTimeout(function() {
          blockVideo.classList.remove('shrink');
        }, 1000)
      }
    });

  }


  console.log(inlineVideoBlocks);
}
