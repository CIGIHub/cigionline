/* global FB */
import 'bootstrap/dist/js/bootstrap.min';
import React from 'react';
import ReactDOM from 'react-dom';
import CookieConsent from './js/components/CookieConsent';
import './css/cigionline.scss';

import addInlineVideoActions from './js/inline_video_block';

$(function() {
  // Facebook Share buttons
  $('.facebook-share-link').on('click', function() {
    const href = $(this).data('url');
    FB.ui(
      {
        method: 'share',
        href,
      },
      function(/* response */) {},
    );
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
          $navSearchInputDropdownCount.append(
            `Results <span>(${data.meta.total_count})<span>`,
          );
          rows.forEach((row) => $navSearchInputDropdownList.append(
            `<li><a href=${row.url}>${row.title}</a></li>`,
          ));
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
  cookieConsentContainer && !document.cookie
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

const bookmarkButtons = document.querySelectorAll('.bookmark-button');
bookmarkButtons.forEach((button) => {
  button.addEventListener('click', (e) => {
    const bookmarkTitle = e.target.getAttribute('data-bookmark-title');
    const url = e.target.getAttribute('data-bookmark-url');
    if (window.sidebar && window.sidebar.addPanel) {
      // Mozilla Firefox Bookmark
      window.sidebar.addPanel(bookmarkTitle, url, '');
    } else if (window.external && ('AddFavorite' in window.external)) {
      // IE Favorite
      window.external.AddFavorite(url, bookmarkTitle);
    } else if (window.opera && window.print) {
      // Opera Hotlist
      this.title = bookmarkTitle;
      return true;
    } else {
      // webkit - safari/chrome
      alert(
        `Press ${navigator.userAgent.toLowerCase().indexOf('mac') !== -1 ? 'Command/Cmd' : 'CTRL'} + D to bookmark this page.`,
      );
    }
    return false;
  });
});
