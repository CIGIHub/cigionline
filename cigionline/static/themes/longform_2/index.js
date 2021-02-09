/* eslint-disable no-unused-vars */

import ScrollReveal from 'scrollreveal';
import Panzoom from '@panzoom/panzoom';
import './css/longform_2.scss';

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

/* sticky header */

const headerEl = document.querySelector('header');
const stickyHeader = document.querySelector('.article-header-sticky');
let headerHeight = null;
let docHeight = null;
let scrolled = null;

window.addEventListener('load', function() {
  headerHeight = headerEl.offsetHeight;
  docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
});

window.addEventListener('scroll', function() {
  const scrollTop = document.querySelector('html').scrollTop;

  scrolled = (scrollTop / docHeight) * 100;
  document.querySelector('progress').setAttribute('value', scrolled);

  if (scrollTop > headerHeight) {
    stickyHeader.classList.add('scrolled');
  } else {
    stickyHeader.classList.remove('scrolled');
  }
});

/* progress bar chapter markers */
$(window).on("load", function () {
  setTimeout(function () {
    var winHeight = $(window).height(),
      docHeight = $(document).height(),
      progressBarContainer = $('.progress-bar'),
      progressBar = $('progress'),
      max, value;

    max = docHeight - winHeight;
    progressBar.attr('max', max);

    if ($('.no-border a').length) {
      // Add the mobile chapter menu
      var mobileMenuContainer = $(document.createElement('div'))
      mobileMenuContainer.addClass('mobile-menu-container');
      var mobileMenu = $(document.createElement('div'));
      mobileMenu.addClass('mobile-menu');
      var mobileMenuTitle = $(document.createElement('div'));
      mobileMenuTitle.addClass('mobile-menu-title');
      mobileMenuTitle.html($('.series-title').html());
      mobileMenu.append(mobileMenuTitle);
      var mobileMenuList = $(document.createElement('ul'));
      mobileMenuList.addClass('mobile-menu-list');
      mobileMenu.append(mobileMenuList);
      mobileMenuContainer.append(mobileMenu);
      $('.longform-2').append(mobileMenuContainer);

      // The button to display the mobile chapter menu
      var mobileMenuButton = $(document.createElement('div'));
      mobileMenuButton.addClass('mobile-menu-button');
      mobileMenuButton.html('<i class="fa fa-list-ul fa-2"></i>');
      mobileMenuButton.click(function () {
        if ($('.mobile-menu-container').css('bottom') === '0px') {
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
      $('.longform-2').append(mobileMenuButton);

      // Loop through all anchors, adding both the tooltips to the
      // progress bar and the mobile chapter menu items.
      $('.no-border a').each(function (ind) {
        var chapterId = $(this).attr('id');
        if (chapterId && max > 0) {
          var label = (ind + 1) + '. ' + $(this).html();

          // Progress bar anchor
          var top = parseInt($(this).offset().top, 10) - 80;
          var percent = ((top / max) * 100).toFixed(4);
          var chapterAnchor = $(document.createElement('a'));
          chapterAnchor.addClass('chapter-anchor');
          chapterAnchor.attr('href', '#' + chapterId);
          chapterAnchor.attr('id', chapterId + '-chapter-anchor');
          chapterAnchor.css({
            'left': percent + '%',
          });
          chapterAnchor.click(function () {
            $('html,body').animate({
              scrollTop: $('#' + chapterId).offset().top - 80,
            }, 1000);
            return false;
          });

          var tooltip = $(document.createElement('div'));
          tooltip.addClass('chapter-anchor-tooltip');
          tooltip.html(label);
          chapterAnchor.append(tooltip);
          progressBarContainer.append(chapterAnchor);

          // Mobile chapter menu link
          var mobileMenuItem = $(document.createElement('li'));
          var mobileMenuItemLink = $(document.createElement('a'));
          mobileMenuItemLink.html(label);
          mobileMenuItemLink.click(function () {
            $('html,body').animate({
              scrollTop: $('#' + chapterId).offset().top,
            }, 1000);
            $('.mobile-menu-button').html('<i class="fa fa-list-ul fa-2"></i>');
            $('.mobile-menu-container').animate({
              'bottom': '-100%',
            }, 500);
            return false;
          });
          mobileMenuItem.append(mobileMenuItemLink);
          mobileMenuList.append(mobileMenuItem);
        }
      });
    }
  }, 250);

  $(window).on('scroll', function () {
    let scrolled = $(window).scrollTop();
    $('progress').attr('value', scrolled);
    if (scrolled >= 65 && $(window).width() >= 768) {
      $('.article-sticky-header').fadeIn();
      $('.progress-bar').addClass('scrolled');
    } else if (scrolled >= 65) {
      $('.mobile-menu-container,.mobile-menu-button').addClass('scrolled');
    } else {
      $('.progress-bar,.mobile-menu-container,.mobile-menu-button').removeClass('scrolled');
      $('.article-sticky-header').fadeOut();
    }

    if ($('body').hasClass('sticky-header') && scrolled >= 70 && $(window).width() >= 768) {
      $('header').addClass('scrolled');
    } else {
      $('header').removeClass('scrolled');
    }

  });
});

$(window).resize(function () {
  // When resizing the window, recalculating the progress bar and
  // chapter anchor values.
  var winHeight = $(window).height(),
    docHeight = $(document).height();

  var max = docHeight - winHeight;
  $('progress').attr('max', max);

  $('.no-border a').each(function () {
    var chapterId = $(this).attr('id');
    if (chapterId && max > 0) {
      var top = parseInt($(this).offset().top, 10) - 80;
      var percent = ((top / max) * 100).toFixed(4);
      $('#' + chapterId + '-chapter-anchor').css({
        'left': percent + '%',
      });
    }
  });
});

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
