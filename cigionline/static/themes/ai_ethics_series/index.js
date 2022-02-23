import './css/ai_ethics_series.scss';

let loaded = false;
const articleMessage = document.getElementById('article-message');
const spinner = document.getElementById('spinner');
const introductionArticle = document.getElementById('introduction-article');
const introductionBody = document.getElementById('introduction-body');
const introductionAuthors = document.getElementById('introduction-authors');
const introductionTitle = document.getElementById('introduction-title');
const footer = document.querySelector('footer');
// load more data from api
function loadArticle() {
  const url = 'http://127.0.0.1:8000/api/series/ai_ethics';
  articleMessage.classList.remove('show');
  spinner.classList.add('show');
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      introductionTitle.innerHTML = data.title;
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
      setTimeout(() => {
        spinner.classList.remove('show');
        introductionArticle.classList.add('show');
      }, 2000);
    });
}

// event listener to load data from api when scrolling to bottom of page
window.addEventListener('scroll', () => {
  if (!loaded) {
    const rect = footer.getBoundingClientRect();
    if (rect.top <= window.innerHeight - 100) {
      loadArticle();
      loaded = true;
    }
  }
});
