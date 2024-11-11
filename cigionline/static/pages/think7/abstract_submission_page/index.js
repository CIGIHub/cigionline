import './css/_abstract_submission_page.scss';

document
  .getElementById('abstractUploadForm')
  .addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch('/abstract-submission/', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        const responseMessage = document.getElementById('responseMessage');

        if (data.status === 'success') {
          responseMessage.innerText = data.message;
          responseMessage.style.color = 'green';
        } else {
          responseMessage.innerText = data.message;
          responseMessage.style.color = 'red';
        }

        responseMessage.style.display = 'block';
      })
      .catch(() => {
        const responseMessage = document.getElementById('responseMessage');
        responseMessage.innerText = 'An unexpected error occurred.';
        responseMessage.style.color = 'red';
        responseMessage.style.display = 'block';
      });
  });
