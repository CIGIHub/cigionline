import React from 'react';
import ReactDOM from 'react-dom';
import TwentiethPage from '../../js/components/TwentiethPage';

import './css/twentieth_page.scss';

const slides = JSON.parse(document.getElementById('slides').textContent);

ReactDOM.render(
  <TwentiethPage slides={slides} />,
  document.getElementById('twentieth-page')
);
