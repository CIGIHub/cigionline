import './css/dph.scss';

document
  .getElementById('subscribe-form-dph')
  .addEventListener('submit', function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    const responseMessage = document.getElementById('response-message');

    fetch(form.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrfToken,
      },
    })
      .then((response) => {
        responseMessage.classList.add('show');
        if (response.status === 200) {
          responseMessage.textContent =
            'Submission successful, please confirm your registration via the message sent to your email address.';
          responseMessage.classList.add('success');
        } else if (response.status === 500) {
          responseMessage.textContent =
            'An unexpected error occurred, please contact websitesupport@cigionline.org';
          responseMessage.classList.add('error');
        } else if (response.status === 400) {
          responseMessage.textContent =
            'Email already registered, please check your inbox for the confirmation message.';
          responseMessage.classList.add('error-email-exists');
        } else {
          responseMessage.textContent = 'An unexpected error occurred, please contact websitesupport@cigionline.org';
          responseMessage.classList.add('error');
        }
      })
      .catch((error) => {
        responseMessage.textContent = 'An unexpected error occurred, please contact websitesupport@cigionline.org';
        responseMessage.classList.add('error');
      });
  });
