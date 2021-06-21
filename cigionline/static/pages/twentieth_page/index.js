import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import TwentiethPage from '../../js/components/TwentiethPage';
import './css/twentieth_page.scss';

const slides = JSON.parse(document.getElementById('slides').textContent);
const initialSlideText = JSON.parse(
  document.getElementById('initial-slide').textContent,
);
const initialSlideNumber = initialSlideText || 'slide-1';
const pageUrl = `/about/${JSON.parse(
  document.getElementById('page-url').textContent,
)}/`;

ReactDOM.render(
  <Router>
    <TwentiethPage
      slides={slides}
      initialSlide={initialSlideNumber}
      pageUrl={pageUrl}
    />
  </Router>,
  document.getElementById('twentieth-page-slides'),
);
