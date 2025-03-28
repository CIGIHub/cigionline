import './css/project_page.scss';

$(function () {
  const policyBriefsLink = document.getElementById('policy-briefs-link');
  policyBriefsLink.addEventListener('click', function (e) {
    e.preventDefault();
    const policyBriefs = document.getElementById('publications');
    policyBriefs.scrollIntoView({ behavior: 'smooth' });
  });
});
