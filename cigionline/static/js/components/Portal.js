import { createPortal } from 'react-dom';

const Portal = ({ children }) => {
  const modalRoot = document.getElementById('slides-nav-arrows');

  return createPortal(children, modalRoot);
};

export default Portal;
