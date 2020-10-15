jQuery(function() {
  const seniorManagement = $('#senior-management');
  const seniorManagementTab = $('#senior-management-tab');

  seniorManagementTab.on('click', function() {
    if (!$(this).hasClass('ajax-loaded')) {
      $.ajax({
        url: '/about/leadership',
        method: 'get',
        data: { show: 'senior-management' },
        success(response) {
          seniorManagement.append(response);
          seniorManagementTab.addClass('ajax-loaded');
        },
      });
    }
  });
});
