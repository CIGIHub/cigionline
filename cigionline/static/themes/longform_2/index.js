/* eslint-disable no-unused-vars */

import ScrollReveal from 'scrollreveal';
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

// fade in article elements

const sr = ScrollReveal();

sr.reveal('.stream-block-blockquote', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'left',
  scale: 1,
});

sr.reveal('.stream-image-block img', {
  delay: 100,
  distance: '0',
  duration: 750,
  scale: 1,
});

sr.reveal('.stream-block-pull-quote.right', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'right',
  scale: 1,
});

sr.reveal('.stream-block-pull-quote.left', {
  delay: 100,
  distance: '50px',
  duration: 750,
  origin: 'left',
  scale: 1,
});

// Hover tooltips
$(function() {
  const body = $('.body');
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

    const position = textLinkPos.left + $(this).width() + 15 - (body.width() - toolTip.width()) / 2;
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

// Sticky header, chapter markers and tooltips for progress bar

let scrolled = null;
let stickyHeader = $('.article-header-sticky');
let headerHeight = null;
let maxHeight = null;
let scrollTop = 0;
let mobileMenuList = $('.mobile-menu-list');;
let mobileMenuButton = $('.mobile-menu-button');
let mobileMenuContainer = $('.mobile-menu-container');;

function setScrollPosition(){
  scrollTop = $(window).scrollTop();
  scrolled = (scrollTop / maxHeight) * 100;
  $('progress').attr('value', scrolled);

  if (scrollTop > headerHeight) {
    $('body').addClass('scrolled');
  } else {
    $('body').removeClass('scrolled');
  }
}

function createMobileMenu() {
  //create mobile menu

  mobileMenuContainer = $(document.createElement('div')).addClass('mobile-menu-container');
  let mobileMenu = $(document.createElement('div')).addClass('mobile-menu');

  let mobileMenuTitle = $(document.createElement('div')).addClass('mobile-menu-title');
  mobileMenuTitle.html($('.series-title').html());
  mobileMenu.append(mobileMenuTitle);

  mobileMenuList = $(document.createElement('ul')).addClass('mobile-menu-list');
  mobileMenu.append(mobileMenuList);

  mobileMenuContainer.append(mobileMenu);
  $('.longform-2-article').append(mobileMenuContainer);

  // The button to display the mobile chapter menu
  mobileMenuButton = $(document.createElement('div')).addClass('mobile-menu-button');
  mobileMenuButton.html('<i class="fa fa-list-ul fa-2"></i>');

  mobileMenuButton.on('click', function () {
    if ($('.mobile-menu-container').css('bottom') == '0px') {
      $(this).html('<i class="fa fa-list-ul fa-2"></i>');
      $('.mobile-menu-container').animate({
        'bottom': '-100%',
      }, 500);
    } else {
      $(this).html('<i class="fa fa-times fa-2"></i>');
      $('.mobile-menu-container').animate({
        'bottom': '0',
      }, 500);
    }
    return false;
  });
  $('.longform-2-article').append(mobileMenuButton);
}

$(window).on('load', function () {
  let docHeight = $(document).height();
  let winHeight = $(window).height()
  headerHeight = $('header').height();

  maxHeight = docHeight - winHeight;

  createMobileMenu();
  setScrollPosition();

  $('.no-border a[name]').each(function (index) {
    //set anchors and add to progress bar
    let chapterName = $(this).attr('name');
    let chapterPosition = $(this).offset().top;
    let horizontalPosition = (chapterPosition/docHeight)*100;

    let chapterAnchor = $(document.createElement('a'));
    let label = (index + 1) + '. ' + $(this).html();

    chapterAnchor.addClass('chapter-anchor');
    chapterAnchor.attr('href', '#' + chapterName);
    chapterAnchor.css({
      'left': horizontalPosition + '%',
    });

    $('.progress-bar').append(chapterAnchor);

    //create tooltips for each anchor title
    let tooltip = $(document.createElement('div')).addClass('chapter-anchor-tooltip');
    tooltip.html(label);
    chapterAnchor.append(tooltip);
    $('.progress-bar').append(chapterAnchor);

    chapterAnchor.on('click', function () {
      $('html,body').animate({
        scrollTop: $('a[name='+chapterName+']').offset().top - headerHeight - 20,
      }, 1000);
      return false;
    });

    //populate menu with chapter content
    let mobileMenuItem = $(document.createElement('li'));
    let mobileMenuItemLink = $(document.createElement('a'));
    mobileMenuItemLink.html(label);
    mobileMenuItemLink.attr('href', '#' + chapterName);

    mobileMenuItemLink.on('click', function () {
      $('html,body').animate({
        scrollTop: $('a[name='+chapterName+']').offset().top,
      }, 1000);
      $('.mobile-menu-button').html('<i class="fa fa-list-ul fa-2"></i>');
      $('.mobile-menu-container').animate({
        'bottom': '-100%',
      }, 500);
      return false;
    });

    mobileMenuItem.append(mobileMenuItemLink);
    mobileMenuList.append(mobileMenuItem);
  });
});

$(window).on('scroll', function () {
  setScrollPosition();
});
