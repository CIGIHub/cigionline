import React from 'react';
import ReactDOM from 'react-dom';
import * as d3 from 'd3';
import Swiper, { Navigation, Pagination } from 'swiper';
import ResearchContentListing from '../../js/components/ResearchContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/research_landing_page.scss';
import 'swiper/swiper-bundle.css';


const readMoreButton = document.getElementById('read-more');
const body = document.getElementById('body');
readMoreButton.addEventListener('click', () => {
  body.classList.toggle('hidden');
});
Swiper.use([Navigation, Pagination]);
const swiperContainer = document.querySelector('.swiper-container');

if (swiperContainer) {
  const researchLandingPageSwiper = new Swiper('.swiper-container', {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },

    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={['Publication']}
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'image_poster_url',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    containerClass={['custom-theme-table']}
    filterTypes={[
      {
        name: 'Event',
        params: [
          {
            name: 'contenttype',
            value: 'Event',
          },
        ],
      },
      {
        name: 'Publication',
        params: [
          {
            name: 'contenttype',
            value: 'Publication',
          },
        ],
      },
      {
        name: 'Multimedia',
        params: [
          {
            name: 'contenttype',
            value: 'Multimedia',
          },
        ],
      },
      {
        name: 'Opinion',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Opinion',
          },
        ],
      },
      {
        name: 'Op-Eds',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Op-Eds',
          },
        ],
      },
      {
        name: 'CIGI in the News',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'CIGI in the News',
          },
        ],
      },
      {
        name: 'News Releases',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'News Releases',
          },
        ],
      },
      {
        name: 'Research Project',
        alias: 'research.ProjectPage',
        aggregationField: 'content_types',
        params: [
          {
            name: 'content_type',
            value: 'research.ProjectPage',
          },
        ],
      },
    ]}
    RowComponent={ResearchContentListing}
    tableColumns={[
      {
        colSpan: 4,
        colTitle: 'Title',
      },
      {
        colSpan: 3,
        colTitle: 'Expert',
      },
      {
        colSpan: 2,
        colTitle: 'Topic',
      },
      {
        colSpan: 2,
        colTitle: 'Type',
      },
      {
        colSpan: 1,
        colTitle: 'PDF',
      },
    ]}
    searchPlaceholder="Search Research by Keyword"
  />,
  document.getElementById('research-search-table')
);
