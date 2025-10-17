const collapsibleParagraphs = document.querySelectorAll(
  '.collapsible-paragraph-block',
);
if (collapsibleParagraphs) {
  collapsibleParagraphs.forEach((paragraph) => {
    console.log(paragraph);
    const toggleButton =
      paragraph.querySelector('h3') ||
      paragraph.querySelector('h2') ||
      paragraph.querySelector('h4');
    toggleButton.addEventListener('click', () => {
      paragraph.classList.toggle('collapsed');
    });
  });
}
