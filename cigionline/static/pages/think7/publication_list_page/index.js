import './css/publication_list_page.scss';

$(function () {
  const select = document.getElementById('taskforce-select');
  const caret = document.getElementById('taskforce-select-caret');

  const form = document.getElementById('taskforce-filter-form');

  function moveCaret() {
    const temp = document.createElement('span');
    temp.style.visibility = 'hidden';
    temp.style.position = 'absolute';
    temp.style.whiteSpace = 'nowrap';
    temp.style.font = window.getComputedStyle(select).font;
    temp.textContent = select.options[select.selectedIndex].text;

    document.body.appendChild(temp);
    const textWidth = temp.offsetWidth;
    document.body.removeChild(temp);

    caret.style.left = `${select.offsetLeft + textWidth + 10}px`;
    caret.style.opacity = 1;
  }

  moveCaret();

  select.addEventListener('change', function () {
    moveCaret();
    if (form) form.submit();
  });

  window.addEventListener('resize', moveCaret);
});
