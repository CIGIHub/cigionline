/* eslint-disable no-unused-vars */
import React from 'react';
import ReactDOM from 'react-dom';
import Swiper, { Navigation, Pagination } from 'swiper';
import PublicationListing from '../../js/components/PublicationListing';
import SearchTable from '../../js/components/SearchTable';
import './css/publication_list_page.scss';
import 'swiper/swiper-bundle.css';

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={['Publication']}
    contentsubtypes={[
      'Books',
      'CIGI Papers',
      'Conference Reports',
      'Essay Series',
      'Policy Briefs',
      'Policy Memos',
      'Special Reports',
    ]}
    fields={['authors', 'pdf_download', 'publishing_date', 'topics']}
    filterTypes={[
      {
        name: 'Books',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Books',
          },
        ],
      },
      {
        name: 'Papers',
        alias: 'CIGI Papers',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'CIGI Papers',
          },
        ],
      },
      {
        name: 'Conference Reports',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Conference Reports',
          },
        ],
      },
      {
        name: 'Essay Series',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Essay Series',
          },
        ],
      },
      {
        name: 'Policy Briefs',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Policy Briefs',
          },
        ],
      },
      {
        name: 'Policy Memos',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Policy Memos',
          },
        ],
      },
      {
        name: 'Special Reports',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Special Reports',
          },
        ],
      },
    ]}
    containerClass={['custom-theme-table', 'table-publications']}
    RowComponent={PublicationListing}
    searchPlaceholder="Search all publications"
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
      },
      {
        colSpan: 2,
        colTitle: 'Topic',
      },
      {
        colSpan: 3,
        colTitle: 'Expert',
      },
      {
        colSpan: 0,
        colTitle: 'PDF',
      },
    ]}
  />,
  document.getElementById('publications-search-table'),
);

Swiper.use([Navigation, Pagination]);
const featuredPublicationsSwiperContainer = document.querySelector(
  '.publication-list-page-featured',
);

if (featuredPublicationsSwiperContainer) {
  const swiperControls = featuredPublicationsSwiperContainer.querySelector('.swiper-controls');
  const publicationListPageSwiper = new Swiper(
    '.publication-list-page-featured',
    {
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

      breakpoints: {
        480: {
          slidesPerView: 2,
          slidesPerGroup: 2,
        },
        768: {
          slidesPerView: 3,
          slidesPerGroup: 3,
        },
        992: {
          slidesPerView: 4,
          slidesPerGroup: 4,
        },
      },
    },
  );
}

const essaySeriesSwiperContainer = document.querySelector('.essay-series');

if (essaySeriesSwiperContainer) {
  const essaySeriesSwiper = new Swiper('.essay-series', {
    slidesPerView: 1,
    slidesPerGroup: 1,
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
