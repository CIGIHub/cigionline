import './css/_event_page.scss';

const eventUploadForm = document.getElementById('eventUploadForm');
eventUploadForm.addEventListener('submit', function (event) {
  event.preventDefault();

  const formData = new FormData(this);
  const responseMessage = document.getElementById('responseMessage');
  responseMessage.classList.remove('success');
  responseMessage.classList.remove('error');
  responseMessage.classList.add('loading');
  responseMessage.innerText = 'Uploading file...';

  fetch(window.location.pathname, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === 'success') {
        responseMessage.innerText = data.message;
        responseMessage.classList.remove('loading');
        responseMessage.classList.remove('error');
        responseMessage.classList.add('success');
        eventUploadForm.querySelector('input[type="file"]').value = '';
      } else {
        responseMessage.innerText = data.message;
        responseMessage.classList.remove('loading');
        responseMessage.classList.remove('success');
        responseMessage.classList.add('error');
      }
    })
    .catch(() => {
      responseMessage.innerText = 'An unexpected error occurred.';
      responseMessage.classList.remove('loading');
      responseMessage.classList.remove('success');
      responseMessage.classList.add('error');
    });
});
