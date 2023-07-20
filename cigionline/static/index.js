/* global FB */
import 'bootstrap/dist/js/bootstrap.min';
import React from 'react';
import ReactDOM from 'react-dom';
import Player from '@vimeo/player';
import CookieConsent from './js/components/CookieConsent';
import './css/cigionline.scss';

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

  const vimeoPlayersArray = [];

  // add event listener to all images inside .card--multimedia
  const multimediaCards = document.querySelectorAll('.card--multimedia');
  multimediaCards.forEach((card) => {
    if (card.classList.contains('has-vimeo')) {
      const cardImage = card.querySelector('.card__image');
      const playIcon =
        card.querySelector('.card__image__play-icon') ||
        card.querySelector('.card__text__play-icon');
      const mmLength = card.querySelector('.card__image__mm-length');
      const img = card.querySelector('img');
      const iframe = card.querySelector('iframe');
      const text = card.querySelector('.card__text');
      const vimeoPlayer = new Player(iframe, { pip: 1 });
      vimeoPlayersArray.push({ player: vimeoPlayer, cardImage });
      playIcon.addEventListener('click', (e) => {
        if (!img.classList.contains('hidden')) {
          const isLargeBreakpoint =
            window.matchMedia('(min-width: 991px)').matches;
          const isMediumBreakpoint =
            window.matchMedia('(min-width: 768px)').matches;
          const isSmallCard = card.classList.contains(
            'card--small--multimedia',
          );
          const isLargeCard = card.classList.contains(
            'card--large--multimedia',
          );
          const isXLargeCard = card.classList.contains(
            'card--xlarge--multimedia',
          );
          playIcon.classList.add('hidden');
          if (mmLength) {
            mmLength.classList.add('hidden');
          }
          img.classList.add('hidden');
          vimeoPlayer.play();
          if (
            (isLargeBreakpoint && !isSmallCard && !isLargeCard) ||
            (isXLargeCard && isMediumBreakpoint)
          ) {
            text.classList.add('hidden');
          }
        }
      });
    }
  });

  function isElementOutOfView(element) {
    const elementRect = element.getBoundingClientRect();
    return (
      elementRect.bottom < 0 ||
      elementRect.right < 0 ||
      elementRect.left > window.innerWidth ||
      elementRect.top > window.innerHeight
    );
  }

  let isScrolling = false;

  function debounceScroll() {
    if (!isScrolling) {
      isScrolling = true;
      setTimeout(() => {
        vimeoPlayersArray.forEach((element) => {
          if (isElementOutOfView(element.cardImage)) {
            element.player.getPaused().then((paused) => {
              if (!paused && !element.cardImage.classList.contains('pop-out')) {
                element.cardImage.classList.add('pop-out');
              }
            });
          } else {
            element.cardImage.classList.remove('pop-out');
          }
        });

        isScrolling = false;
      }, 1000);
    }
  }

  window.addEventListener('scroll', debounceScroll);
});

const globalNav = document.getElementById('global-nav');
const header = document.querySelector('header:not(.small)');

function handleHeaderSize() {
  const scrollPosition = Math.round(window.scrollY);
  const scrollPoint = 66;
  if (scrollPosition > scrollPoint) {
    header.classList.add('scrolled');
    globalNav.classList.add('scrolled-nav');
  } else if (scrollPosition + 20 < scrollPoint) {
    header.classList.remove('scrolled');
    globalNav.classList.remove('scrolled-nav');
  }
}

window.addEventListener('scroll', handleHeaderSize);

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
