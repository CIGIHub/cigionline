import './css/think7.scss';
// import React from 'react';
// import ReactDOM from 'react-dom';
// import CookieConsent from '../../js/components/CookieConsent';

$(function () {
  document
    .getElementById('open-menu-btn')
    .addEventListener('click', function (e) {
      e.stopPropagation();
      this.classList.toggle('open');

      const dropdownMenu = document.getElementById('dropdown-menu');
      dropdownMenu.classList.toggle('show');

      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', !isExpanded);
    });
});

// const cookieConsentContainer = document.getElementById(
//   'cigi-cookie-consent-container',
// );
// if (
//   cookieConsentContainer &&
//   !document.cookie
//     .split(';')
//     .some((item) => item.includes('cigionline.accept.privacy.notice=1'))
// ) {
//   ReactDOM.render(<CookieConsent />, cookieConsentContainer);
// }
