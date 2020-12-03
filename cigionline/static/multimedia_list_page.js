jQuery(function() {
  const multimediaList = $('#multimedia-list-section');
  
  function paginate() {
    const pagination = $('.pagination-links-numbered');
    pagination.find('a').on('click', function(event) {
      event.preventDefault();
      const page = $(this).attr('data-page');
      console.log(page);
      $.ajax({
        url: '/multimedia/',
        method: 'get',
        data: { page },
        success(response) {
          multimediaList.empty().append(response);
          paginate();
        },
      });
    });
  }

  paginate();
});
