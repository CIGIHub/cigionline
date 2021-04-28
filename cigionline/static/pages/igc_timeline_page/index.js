import './css/igc_timeline_page.scss';
/* eslint-disable guard-for-in */

const witnessesHash = {};
const outcomesHash = {};

function activateTab(hash, buttonElement, type) {
  let contentClass;

  if (type === 'witnesses') {
    contentClass = '.timeline-witnesses';
  } else if (type === 'outcomes') {
    contentClass = '.timeline-outcomes';
  }

  const dateString = buttonElement.text().trim();
  const timelineDateString = buttonElement
    .closest('.igc-timeline')
    .find('.timeline-date')
    .text()
    .trim();
  const selectedContent = hash[timelineDateString][dateString].content;

  buttonElement.find('time').addClass('active');
  selectedContent.addClass('active');
  selectedContent.closest(contentClass).height(selectedContent.height());

  for (const dateKey in hash[timelineDateString]) {
    if (dateKey !== dateString) {
      hash[timelineDateString][dateKey].content.removeClass('active');
      hash[timelineDateString][dateKey].date.find('time').removeClass('active');
    }
  }
}

function appendDates(dates, type, hash, timelineDateString) {
  dates.each(function() {
    let dateClass;
    let contentClass;
    let containerClass;

    if (type === 'witnesses') {
      dateClass = '.witnesses-date';
      contentClass = '.witnesses';
      containerClass = '.witnesses-dates';
    } else if (type === 'outcomes') {
      dateClass = '.outcomes-date';
      contentClass = '.outcomes-text';
      containerClass = '.outcomes-dates';
    }

    const date = $(this).find(dateClass);
    const dateString = date.find('time').text().trim();

    hash[timelineDateString][dateString] = {
      content: $(this).find(contentClass),
      date,
    };

    date.appendTo($(this).closest('.timeline-contents').find(containerClass));
  });
}

function addActive(hash, type) {
  let containerClass;
  if (type === 'witnesses') {
    containerClass = '.timeline-witnesses';
  } else if (type === 'outcomes') {
    containerClass = '.timeline-outcomes';
  }

  for (const timelineDateKey in hash) {
    const firstDateKey = Object.keys(hash[timelineDateKey])[0];
    const container = hash[timelineDateKey][firstDateKey];

    container.content.addClass('active');
    container.date.find('time').addClass('active');
    container.content
      .closest(containerClass)
      .height(container.content.height());
  }
}

// use witnessesHash to link date elements to witnesses elements
function initializeTimeline() {
  $('.igc-timeline').each(function() {
    const timelineDate = $(this).find('.timeline-date');
    const witnessDates = $(this).find('.witnesses-date-block');
    const outcomesDates = $(this).find('.outcomes-block');
    const timelineDateString = timelineDate.text().trim();
    witnessesHash[timelineDateString] = {};
    outcomesHash[timelineDateString] = {};

    appendDates(witnessDates, 'witnesses', witnessesHash, timelineDateString);
    appendDates(outcomesDates, 'outcomes', outcomesHash, timelineDateString);
  });

  // add active class to first date in list and modify height of container
  addActive(witnessesHash, 'witnesses');
  addActive(outcomesHash, 'outcomes');
}

initializeTimeline();

// add active class to date clicked and its corresponding witnesses element
// remove active class from other dates and their corresponding witnesses
$('.witnesses-date').on('click', function() {
  activateTab(witnessesHash, $(this), 'witnesses');
});

$('.outcomes-date').on('click', function() {
  activateTab(outcomesHash, $(this), 'outcomes');
});
