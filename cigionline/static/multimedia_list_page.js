jQuery(function() {
  const multimediaList = $('#multimedia-list-section');
  const loaderSpinner = $('.loader-spinner');

  function paginate() {
    const pagination = $('.pagination-links-numbered');
    pagination.find('a').on('click', function(event) {
      const page = $(this).attr('data-page');

      event.preventDefault();
      loaderSpinner.addClass('show');

      $.ajax({
        url: '/multimedia/',
        method: 'get',
        data: { page },
        success(response) {
          multimediaList.empty().append(response);
          paginate();
          loaderSpinner.removeClass('show');
          document.querySelector('#multimedia-list-section').scrollIntoView({
            behavior: 'smooth',
          });
        },
      });
    });
  }

  paginate();
});
