import React from 'react';
import ReactDOM from 'react-dom';
import TwentiethPage from '../../js/components/TwentiethPage';

import './css/twentieth_page.scss';

const slides = JSON.parse(document.getElementById('slides').textContent);
const initialSlideText = document.getElementById('initial-slide').textContent;
const initialSlide = initialSlideText
  ? Number(initialSlideText.charAt(initialSlideText.length - 2)) - 1
  : 1;

ReactDOM.render(
  <TwentiethPage slides={slides} initialSlide={initialSlide} />,
  document.getElementById('twentieth-page-slides'),
);
