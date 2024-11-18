import './css/_abstract_submission_page.scss';

const abstractUploadForm = document.getElementById('abstractUploadForm');
abstractUploadForm
  .addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const responseMessage = document.getElementById('responseMessage');
    responseMessage.classList.add('loading');
    responseMessage.innerText = 'Uploading file...';

    fetch('/abstract-submission/', {
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
          abstractUploadForm.querySelector('input[type="file"]').value = '';
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
