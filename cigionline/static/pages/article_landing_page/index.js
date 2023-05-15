/* eslint-disable no-unused-vars */

import Swiper, { Navigation, Pagination } from 'swiper';
import React from 'react';
import ReactDOM from 'react-dom';
import OpinionListing from '../../js/components/OpinionListing';
import SearchTable from '../../js/components/SearchTable';

import 'swiper/swiper-bundle.css';
import './css/article_landing_page.scss';
import SearchResultCard from '../../js/components/SearchResultCard';
import ArticleSeriesList from '../../js/components/ArticleSeriesList';

Swiper.use([Navigation, Pagination]);

const swiperContainerOpinions = document.querySelector(
  '.swiper-container--opinions',
);
const swiperContainerOpinionSeries = document.querySelector(
  '.swiper-container--opinion-series',
);
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
    contenttypes={['Opinion']}
    contentsubtypes={['Interviews', 'Op-Eds', 'Opinion']}
    fields={['authors', 'image_hero_url', 'publishing_date', 'topics']}
    containerClass={['custom-theme-table', 'table-opinions']}
    RowComponent={SearchResultCard}
    RowComponentList={OpinionListing}
    searchPlaceholder="Search all opinions"
    tableColumns={[
      {
        colSpan: 6,
        colTitle: 'Title',
        colClass: 'title',
      },
      {
        colSpan: 3,
        colTitle: 'Author',
        colClass: 'authors',
      },
      {
        colSpan: 3,
        colTitle: 'Topic',
        colClass: 'topics',
      },
      {
        colSpan: 1,
        colTitle: 'More',
        colClass: 'more',
      },
    ]}
  />,
  document.getElementById('opinions-search-table'),
);

ReactDOM.render(
  <ArticleSeriesList />,
  document.getElementById('article-landing-page__opinion-series-listing'),
);

const navItems = document.querySelectorAll('.nav-link');
const pageLabel = document.getElementById('page-label');
navItems.forEach((item) => {
  item.addEventListener('click', () => {
    pageLabel.innerHTML = item.innerHTML;
  });
});
