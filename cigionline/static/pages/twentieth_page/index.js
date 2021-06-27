import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import TwentiethPage from '../../js/components/TwentiethPage';
import './css/twentieth_page.scss';

const slides = JSON.parse(document.getElementById('slides').textContent);
const initialSlideSlug =
  JSON.parse(document.getElementById('initial-slide').textContent) ||
  slides[0].slug;
const pageUrl = `/about/${JSON.parse(
  document.getElementById('page-url').textContent
)}/`;
const socialButton = $('#open-share-btn');
const socialMenu = $('#social-share-list');
socialButton.on('click', function () {
  $(this).toggleClass('open');
  if ($(this).hasClass('open')) {
    socialMenu.animate({ opacity: 1, width: '100px', marginRight: 0 });
  } else {
    socialMenu.animate({ opacity: 0, width: '40px', marginRight: '-20px' });
  }
});

ReactDOM.render(
  <Router>
    <TwentiethPage
      slides={slides}
      initialSlideSlug={initialSlideSlug}
      pageUrl={pageUrl}
    />
  </Router>,
  document.getElementById('twentieth-page-slides')
);
