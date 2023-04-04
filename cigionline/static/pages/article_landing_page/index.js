/* eslint-disable no-unused-vars */

import Swiper, { Navigation, Pagination } from 'swiper';
import React from 'react';
import ReactDOM from 'react-dom';
import OpinionListing from '../../js/components/OpinionListing';
import SearchTable from '../../js/components/SearchTable';

import 'swiper/swiper-bundle.css';
import './css/article_landing_page.scss';

Swiper.use([Navigation, Pagination]);

const swiperContainerOpinions = document.querySelector('.swiper-container--opinions');
const swiperContainerOpinionSeries = document.querySelector('.swiper-container--opinion-series');
if (swiperContainerOpinions) {
  const opinionsSwiper = new Swiper(swiperContainerOpinions, {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next-opinions',
      prevEl: '.swiper-button-prev-opinions',
    },

    pagination: {
      el: '.swiper-pagination-opinions',
      clickable: true,
    },
  });
}

if (swiperContainerOpinionSeries) {
  const opinionSeriesSwiper = new Swiper(swiperContainerOpinionSeries, {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next-opinion-series',
      prevEl: '.swiper-button-prev-opinion-series',
    },

    pagination: {
      el: '.swiper-pagination-opinion-series',
      clickable: true,
    },
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={[
      'Opinion',
    ]}
    contentsubtypes={[
      'Interviews',
      'Op-Eds',
      'Opinion',
    ]}
    fields={[
      'authors',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
      'table-opinions',
    ]}
    RowComponent={OpinionListing}
    RowComponentList={OpinionListing}
    searchPlaceholder="Search all opinions"
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
      colClass: 'title',
    }, {
      colSpan: 3,
      colTitle: 'Author',
      colClass: 'authors',
    }, {
      colSpan: 3,
      colTitle: 'Topic',
      colClass: 'topics',
    }, {
      colSpan: 1,
      colTitle: 'More',
      colClass: 'more',
    }]}
  />,
  document.getElementById('opinions-search-table'),
);
