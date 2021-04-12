/* global FB */
import 'bootstrap/dist/js/bootstrap.bundle';
import React from 'react';
import ReactDOM from 'react-dom';
import CookieConsent from './js/components/CookieConsent';
import './css/cigionline.scss';

import addInlineVideoActions from './js/inline_video_block';

$(function() {
  // MAIN NAVIGATION SCROLL
  let scrollTop = 0;

  $(window).on('scroll', function() {
    scrollTop = $(window).scrollTop();
    if (scrollTop >= 66) {
      $('header').addClass('scrolled');
      $('#global-nav').addClass('scrolled-nav');
    } else {
      $('header').removeClass('scrolled');
      $('#global-nav').removeClass('scrolled-nav');
    }
  });

  // MAIN DROPDOWN MENU ACCORDIONS
  const accordions = document.getElementsByClassName('accordion');
  for (let i = 0; i < accordions.length; i += 1) {
    accordions[i].addEventListener('click', function() {
      this.classList.toggle('active');
      const panel = this.nextElementSibling;
      if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
      } else {
        panel.style.maxHeight = `${panel.scrollHeight}px`;
      }
    });
  }

  // SEARCH BAR AND MENU OPEN
  const $openSearchBtn = $('#open-search-btn');
  const $openMenuBtn = $('#open-menu-btn');
  const openMenuClass = 'opened-popup';

  $openSearchBtn.on('click', function() {
    $(this).toggleClass('open');
    $('#popup-search').toggleClass(openMenuClass);
    $('body').toggleClass('disable-scroll');
  });

  $openMenuBtn.on('click', function() {
    $(this).toggleClass('open');
    $('#popup-menu').toggleClass(openMenuClass);
    $('body').toggleClass('disable-scroll');
  });

  $(document).on('click', `.${openMenuClass}`, function() {
    $(this).removeClass(openMenuClass);
    $openSearchBtn.removeClass('open');
    $openMenuBtn.removeClass('open');
    $('body').toggleClass('disable-scroll');
  });

  $('.custom-popup-inner').on('click', function(e) {
    e.stopPropagation();
  });

  // Facebook Share buttons
  $('.facebook-share-link').on('click', function() {
    const href = $(this).data('url');
    FB.ui({
      method: 'share',
      href,
    }, function(/* response */) {});
  });
});

addInlineVideoActions();

const cookieBannerContainer = document.getElementById('cigi-cookie-banner-container');
if (cookieBannerContainer) {
  ReactDOM.render(
    <CookieConsent />,
    cookieBannerContainer,
  );
}
