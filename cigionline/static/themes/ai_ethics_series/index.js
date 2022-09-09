import './css/ai_ethics_series.scss';

let loaded = false;
const articleMessage = document.getElementById('article-message');
const spinner = document.getElementById('spinner');
const introductionArticle = document.getElementById('introduction-article');
const introductionBody = document.getElementById('introduction-body');
const introductionAuthors = document.getElementById('introduction-authors');
const introductionTitle = document.getElementById('introduction-title');
const introductionDate = document.getElementById('introduction-date');
const introductionImage = document.getElementById('introduction-image');
const introductionReadMore = document.getElementById('introduction-read-more');
const introductionLoadingBackground = document.getElementById('introduction-loading-background');
const footer = document.querySelector('footer');

function loadArticle() {
  const url = '/api/series/ai_ethics';
  articleMessage.classList.remove('show');
  spinner.classList.add('show');
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      data.authors.forEach((author) => {
        const authorElement = document.createElement('li');
        const authorLink = document.createElement('a');
        authorLink.href = author.url;
        authorLink.innerHTML = author.title;
        authorElement.appendChild(authorLink);
        introductionAuthors.appendChild(authorElement);
      });
      introductionTitle.innerHTML = data.title;
      introductionBody.innerHTML = data.body;
      introductionDate.innerHTML = data.date;
      introductionImage.src = data.image;
      introductionArticle.classList.add('loading');
      introductionLoadingBackground.classList.add('show');
      setTimeout(() => {
        spinner.classList.remove('show');
        introductionArticle.classList.remove('loading');
        introductionLoadingBackground.classList.remove('show');
        introductionArticle.classList.add('show');
        introductionReadMore.classList.add('show');
      }, 1000);
    });
}

window.addEventListener('scroll', () => {
  if (!loaded) {
    const rect = footer.getBoundingClientRect();
    if (rect.top <= window.innerHeight + 100) {
      loadArticle();
      loaded = true;
    }
  }
});
