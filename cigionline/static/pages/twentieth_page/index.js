import React from 'react';
import ReactDOM from 'react-dom';
import TwentiethPage from '../../js/components/TwentiethPage';
import { BrowserRouter as Router } from 'react-router-dom';
import './css/twentieth_page.scss';

const slides = JSON.parse(document.getElementById('slides').textContent);
const initialSlideText = document.getElementById('initial-slide').textContent;
const initialSlide = initialSlideText
  ? Number(initialSlideText.charAt(initialSlideText.length - 2)) - 1
  : 1;

ReactDOM.render(
  <Router>
    <TwentiethPage slides={slides} initialSlide={initialSlide} />
  </Router>,
  document.getElementById('twentieth-page-slides'),
);
