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
    FB.ui({
      method: 'share',
      href,
    }, function(/* response */) {});
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
