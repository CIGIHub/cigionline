import { createPortal } from 'react-dom';

const MenuPortal = ({ children }) => {
  const modalRoot = document.getElementById('annual-report-interactives-menu');

  return createPortal(children, modalRoot);
};

export default MenuPortal;
