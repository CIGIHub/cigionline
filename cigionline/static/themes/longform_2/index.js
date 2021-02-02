/* eslint-disable no-unused-vars */

import Panzoom from '@panzoom/panzoom';
import './css/longform_2.scss';

// Image Scroll stream block
const panzoomContainers = Array.from(document.getElementsByClassName('stream-image-scroll-block'));
const panzoomImg = [];
const panzoomScrollbar = [];
const panzoomArrow = [];
const panzoomScrollbarWrapper = [];

function setScrollBarWidth(index) {
  panzoomScrollbar[index].style.width = `${Math.min((panzoomContainers[index].offsetWidth / panzoomImg[index].offsetWidth) * 100, 100)}%`;
}

function moveScrollBar(x, index) {
  panzoomScrollbar[index].style.transform = `matrix(1,0,0,1,${x},0)`;
}

function moveImage(x, index) {
  panzoomImg[index].style.transform = `matrix(1,0,0,1,${x},0)`;
}

function resizeUpdate() {
  panzoomContainers.forEach(function(panzoomContainer, index) {
    setScrollBarWidth(index);
    if (panzoomImg[index].offsetWidth <= panzoomContainer.offsetWidth) {
      panzoomScrollbarWrapper[index].style.display = 'none';
      panzoomArrow[index].style.display = 'none';
    } else {
      panzoomScrollbarWrapper[index].style.display = 'block';
      panzoomArrow[index].style.display = 'block';
    }
  });
}

panzoomContainers.forEach(function(panzoomContainer, index) {
  panzoomImg[index] = panzoomContainer.querySelector('img');
  panzoomScrollbar[index] = panzoomContainer.querySelector('.panzoom-scrollbar-inner');
  panzoomScrollbarWrapper[index] = panzoomContainer.querySelector('.panzoom-scrollbar-outer');
  panzoomArrow[index] = panzoomContainer.querySelector('.panzoom-arrow');
  const panzoomImgInstance = Panzoom(panzoomImg[index], { contain: 'outside', disableYAxis: true });
  const panzoomScrollbarInstance = Panzoom(panzoomScrollbar[index], { contain: 'inside', disableYAxis: true });

  setScrollBarWidth(index);

  panzoomImg[index].addEventListener('panzoompan', function(event) {
    const x = Math.abs(
      (panzoomScrollbar[index].offsetWidth / panzoomContainers[index].offsetWidth) * event.detail.x,
    );
    moveScrollBar(x, index);
  });

  panzoomScrollbar[index].addEventListener('panzoompan', function(event) {
    const x = Math.abs(
      (panzoomContainers[index].offsetWidth / panzoomScrollbar[index].offsetWidth) * event.detail.x,
    ) * -1;
    moveImage(x, index);
  });
});

window.addEventListener('resize', resizeUpdate);

// Hover tooltips
$(function() {
  $('.text-bubble-link').on('mouseenter touchstart', function() {
    const textLinkPos = $(this).position();
    const toolTipID = $(this).find('a').attr('name');
    const toolTip = $(`.${toolTipID}`);
    const triangle = toolTip.find('.triangle');

    function canShowAbove(position, element) {
      const newTop = position - element.height();
      const scrollTop = $(window).scrollTop();
      return (newTop - scrollTop > 150); // Extra 80 for padding, and 70 for sticky headers.
    }

    if (canShowAbove($(this).offset().top, toolTip)) {
      toolTip.css({
        top: textLinkPos.top - 78 - toolTip.height(),
        left: 0,
      }).fadeIn(250);
      triangle.removeClass('triangle-top');
    } else {
      toolTip.css({
        top: textLinkPos.top + 40,
        left: 0,
      }).fadeIn(250);
      triangle.addClass('triangle-top');
    }

    const position = textLinkPos.left + $(this).width() - 30;
    triangle.css({ left: position });
  });

  $('.tool-tip-block').on('mouseleave', function() {
    $(this).fadeOut(250);
  });

  $('.tooltip-close').on('click', function() {
    const toolTip = $(this).parent();
    toolTip.hide();
  });
});
