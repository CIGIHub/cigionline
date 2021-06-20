import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import PropTypes from 'prop-types';
const Portal = ({ children }) => {
  const modalRoot = document.getElementById('slides-nav-arrows');

  return createPortal(children, modalRoot);
};

export default Portal;
