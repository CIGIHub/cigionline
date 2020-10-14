jQuery(function() {
  const pager = $('.pager-alphabet');

  pager.find('a').on('click', function(event) {
    event.preventDefault();
    const letter = $(this).text() === 'Show All' ? '' : $(this).text();

    $.ajax({
      url: '/about/staff',
      method: 'get',
      data: { letter },
      success(response) {
        $('#staff-directory-list').fadeOut('slow', function() {
          $(this).empty().prepend(response).fadeIn();
        });
      },
    });
  });
});
