import './css/_event_page.scss';

function getCSRFToken() {
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  return input ? input.value : null;
}

const CSRFToken = getCSRFToken();
const h2 = document.querySelectorAll('h2');
if (h2) {
  h2.forEach((h2Element) => {
    const id = h2Element.innerText.trim().toLowerCase().replace(/\s+/g, '-');
    h2Element.setAttribute('id', id);
  });
}
// const eventUploadForm = document.getElementById('eventUploadForm');
// eventUploadForm.addEventListener('submit', function (event) {
//   event.preventDefault();

//   const formData = new FormData(this);
//   const responseMessage = document.getElementById('responseMessage');
//   responseMessage.classList.remove('success');
//   responseMessage.classList.remove('error');
//   responseMessage.classList.add('loading');
//   responseMessage.innerText = 'Uploading file...';

//   fetch(window.location.pathname, {
//     method: 'POST',
//     headers: {
//       'X-Requested-With': 'XMLHttpRequest',
//       'X-CSRFToken': CSRFToken,
//     },
//     body: formData,
//     credentials: 'same-origin',
//   })
//     .then((response) => response.json())
//     .then((data) => {
//       if (data.status === 'success') {
//         responseMessage.innerText = data.message;
//         responseMessage.classList.remove('loading');
//         responseMessage.classList.remove('error');
//         responseMessage.classList.add('success');
//         eventUploadForm.querySelector('input[type="file"]').value = '';
//       } else {
//         responseMessage.innerText = data.message;
//         responseMessage.classList.remove('loading');
//         responseMessage.classList.remove('success');
//         responseMessage.classList.add('error');
//       }
//     })
//     .catch(() => {
//       responseMessage.innerText = 'An unexpected error occurred.';
//       responseMessage.classList.remove('loading');
//       responseMessage.classList.remove('success');
//       responseMessage.classList.add('error');
//     });
// });
