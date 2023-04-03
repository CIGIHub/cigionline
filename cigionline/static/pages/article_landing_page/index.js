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
    searchPlaceholder="Search all opinions"
    tableColumns={[{
      colSpan: 6,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Author',
    }, {
      colSpan: 3,
      colTitle: 'Topic',
    }]}
  />,
  document.getElementById('opinions-search-table'),
);
