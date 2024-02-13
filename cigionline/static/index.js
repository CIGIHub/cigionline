/* global FB */
/* global fbq */
import 'bootstrap/dist/js/bootstrap.bundle';
import React from 'react';
import ReactDOM from 'react-dom';
import CookieConsent from './js/components/CookieConsent';
import './css/cigionline.scss';

import addInlineVideoActions from './js/inline_video_block';

$(function() {
  // MAIN NAVIGATION SCROLL
  let scrollTop = 0;
  const header = $('header:not(.small)');
  const globalNav = header.find('#global-nav');

  $(window).on('scroll', function() {
    scrollTop = $(window).scrollTop();
    if (scrollTop >= 66) {
      header.addClass('scrolled');
      globalNav.addClass('scrolled-nav');
    } else {
      header.removeClass('scrolled');
      globalNav.removeClass('scrolled-nav');
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
    $openMenuBtn.removeClass('open');
    if ($('#popup-menu').hasClass(openMenuClass)) {
      $('body').addClass('disable-scroll');
    } else {
      $('body').toggleClass('disable-scroll');
    }
    $('#popup-menu').removeClass(openMenuClass);
    $('#popup-search').toggleClass(openMenuClass);
    setTimeout(function() {
      document.getElementById('nav-search-input').focus();
    }, 100);
  });

  $openMenuBtn.on('click', function() {
    $(this).toggleClass('open');
    $openSearchBtn.removeClass('open');
    if ($('#popup-search').hasClass(openMenuClass)) {
      $('body').addClass('disable-scroll');
    } else {
      $('body').toggleClass('disable-scroll');
    }
    $('#popup-search').removeClass(openMenuClass);
    $('#popup-menu').toggleClass(openMenuClass);
  });

  $(document).on('click', `.${openMenuClass}`, function() {
    $(this).removeClass(openMenuClass);
    $openSearchBtn.removeClass('open');
    $openMenuBtn.removeClass('open');
    $('body').removeClass('disable-scroll');
  });

  $('.custom-popup-inner').on('click', function(e) {
    e.stopPropagation();
  });

  $('.dropdown.custom-dropdown.keep-open').on('hide.bs.dropdown', function(e) {
    if (e.clickEvent !== undefined) {
      const target = $(e.clickEvent.target);
      if (target.hasClass('keep-open') || target.parents('.keep-open').length) {
        return false; // returning false should stop the dropdown from hiding.
      }
    }
    return true;
  });

  const $navSearchInput = $('#nav-search-input');
  const $navSearchInputDropdown = $('#nav-search-input-dropdown');
  const $navSearchInputDropdownList = $('#nav-search-input-dropdown-list');
  const $navSearchInputDropdownCount = $('#nav-search-input-dropdown-count');
  $navSearchInput.on('input', function(e) {
    const searchValue = e.target.value;
    if (searchValue) {
      $navSearchInputDropdown.addClass('show');
      const uri = `/api/search/?limit=6&offset=0&sort=relevance&searchtext=${searchValue}`;
      fetch(encodeURI(uri))
        .then((res) => res.json())
        .then((data) => {
          const rows = data.items.filter(
            (v, i, a) => a.findIndex((t) => t.id === v.id) === i,
          );
          $navSearchInputDropdownList.empty();
          $navSearchInputDropdownCount.empty();
          $navSearchInputDropdownCount.append(`Results <span>(${data.meta.total_count})<span>`);
          rows.forEach((row) => $navSearchInputDropdownList.append(`<li><a href=${row.url}>${row.title}</a></li>`));
        });
    } else {
      $navSearchInputDropdown.removeClass('show');
    }
  });
});

addInlineVideoActions();

const cookieConsentContainer = document.getElementById('cigi-cookie-consent-container');
if (cookieConsentContainer && !document.cookie.split(';').some((item) => item.includes('cigionline.accept.privacy.notice=1'))) {
  ReactDOM.render(
    <CookieConsent />,
    cookieConsentContainer,
  );
}

// Add Meta pixel tracking to all elements with class 'track-cta'
const buttons = document.getElementsByClassName('track-cta');
for (let i = 0; i < buttons.length; i += 1) {
  buttons[i].addEventListener('click', function() {
    const dataCTA = this.getAttribute('data-cta').split('-');
    const cta = dataCTA[0];
    const action = dataCTA.length > 1 ? dataCTA[1] : 'click';
    fbq('track', 'CTA Click', {
      cta_type: cta,
      cta_action: action,
    });
  });
}
