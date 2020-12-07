/*
  This provides pagination for content list pages such as multimedia_list
  and publication_list. Pages that use this script will need the following
  elements inside {% block content %}:

  1. A "pagination" element that includes the pagination_numbered.html with
    the content variable populated. EX:
    <div class="pagination">
      {% include "includes/pagination_numbered.html" with content=multimedia %}
    </div>

  2. A loader element with the class "loader-spinner":
    <div class="loader-spinner">
      <img src="{% static 'assets/loader_spinner.gif' %}"></img>
    </div>

  The function takes two parameters:
    listId: the id of the content list element, EX: '#multimedia-list-section'
    url: the AJAX url, EX: '/multimedia/'
*/

export default function paginate(listId, url) {
  const loaderSpinner = $('.loader-spinner');
  const pagination = $('.pagination-links-numbered');
  pagination.find('a').on('click', function(event) {
    const page = $(this).attr('data-page');

    event.preventDefault();
    loaderSpinner.addClass('show');

    $.ajax({
      url,
      method: 'get',
      data: { page },
      success(response) {
        $(listId).empty().append(response);
        paginate(listId, url);
        loaderSpinner.removeClass('show');
        document.querySelector(listId).scrollIntoView({
          behavior: 'smooth',
        });
      },
    });
  });
}
