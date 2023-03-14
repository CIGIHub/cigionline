/* global FB */
import 'bootstrap/dist/js/bootstrap.min';
import React from 'react';
import ReactDOM from 'react-dom';
import videojs from 'video.js';
import CookieConsent from './js/components/CookieConsent';
import './css/cigionline.scss';
import 'video.js/dist/video-js.min.css';
import 'video.js/dist/video.min';
import 'videojs-youtube/dist/Youtube.min';

import addInlineVideoActions from './js/inline_video_block';

$(function () {
  // Facebook Share buttons
  $('.facebook-share-link').on('click', function () {
    const href = $(this).data('url');
    FB.ui(
      {
        method: 'share',
        href,
      },
      function (/* response */) {},
    );
  });

  const $navSearchInput = $('#nav-search-input');
  const $navSearchInputDropdown = $('#nav-search-input-dropdown');
  const $navSearchInputDropdownList = $('#nav-search-input-dropdown-list');
  const $navSearchInputDropdownCount = $('#nav-search-input-dropdown-count');
  $navSearchInput.on('input', function (e) {
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
          $navSearchInputDropdownCount.append(
            `Results <span>(${data.meta.total_count})<span>`,
          );
          rows.forEach((row) =>
            $navSearchInputDropdownList.append(
              `<li><a href=${row.url}>${row.title}</a></li>`,
            ),
          );
        });
    } else {
      $navSearchInputDropdown.removeClass('show');
    }
  });
});

addInlineVideoActions();

const cookieConsentContainer = document.getElementById(
  'cigi-cookie-consent-container',
);
if (
  cookieConsentContainer &&
  !document.cookie
    .split(';')
    .some((item) => item.includes('cigionline.accept.privacy.notice=1'))
) {
  ReactDOM.render(<CookieConsent />, cookieConsentContainer);
}

const copyTextButtons = document.querySelectorAll('.copy-text-button');
copyTextButtons.forEach((button) => {
  button.addEventListener('click', (e) => {
    const input = e.target.nextElementSibling;
    input.select();
    input.setSelectionRange(0, 99999); // For mobile devices
    navigator.clipboard.writeText(input.value);
  });
});

const dropdownMenuButton = document.getElementById('dropdown-menu-btn');
const dropdownSearchButton = document.getElementById('dropdown-search-btn');
const dropdownMenuFull = document.getElementById(
  'header--top-bar__dropdown-menu--full',
);
const body = document.querySelector('body');
dropdownMenuButton.addEventListener('click', (e) => {
  if (window.innerWidth < 576) {
    if (dropdownMenuButton.getAttribute('aria-expanded') === 'false') {
      dropdownMenuFull.classList.remove('show');
      body.classList.remove('disable-scroll');
    } else {
      dropdownMenuFull.classList.add('show');
      body.classList.add('disable-scroll');
    }
  }
});
dropdownSearchButton.addEventListener('click', (e) => {
  if (window.innerWidth < 576) {
    if (dropdownMenuFull.classList.contains('show')) {
      dropdownMenuFull.classList.remove('show');
      body.classList.remove('disable-scroll');
    }
  }
});
window.addEventListener('resize', (e) => {
  if (window.innerWidth > 576) {
    dropdownMenuFull.classList.remove('show');
    body.classList.remove('disable-scroll');
  }
});

// add event listener to all images inside .card--multimedia
const multimediaCards = document.querySelectorAll('.card--multimedia');
multimediaCards.forEach((card) => {
  const playIcon = card.querySelector('.card__image__play-icon');
  const mmLength = card.querySelector('.card__image__mm-length');
  const video = card.querySelector('.video-js');
  const blockId = video.dataset.blockId;
  const player = videojs(`video-js-${blockId}`, {
    controls: 'false',
    autoplay: 'false',
    techOrder: ['youtube'],
    sources: [{ type: 'video/youtube', src: video.dataset.youtubeUrl }],
    enablejsapi: 1,
    origin: window.location.origin,
  });
  player.on('play', () => {
    playIcon.style.display = 'none';
    mmLength && (mmLength.style.display = 'none');
  });
});
