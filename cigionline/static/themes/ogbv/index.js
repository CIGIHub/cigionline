/* global projectId */
/* eslint-disable no-unused-vars */

import React from 'react';
import ReactDOM from 'react-dom';
import Swiper from 'swiper';
import { Navigation, Pagination } from 'swiper/modules'; // eslint-disable-line import/no-unresolved
import ProjectContentListing from '../../js/components/ProjectContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/ogbv.scss';
import 'swiper/swiper-bundle.css';

Swiper.use([Navigation, Pagination]);
const swiperContainer = document.querySelector('.swiper-container');

if (swiperContainer) {
  const OGBVPageSwiper = new Swiper('.swiper-container', {
    slidesPerView: 2,
    slidesPerGroup: 2,
    spaceBetween: 40,
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
      horizontalClass: 'swiper-pagination-horizontal-styles-disabled',
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
    },
  });
}

const endpointParams = [];
if (projectId) {
  endpointParams.push({
    paramName: 'project',
    paramValue: projectId,
  });
}

ReactDOM.render(
  <SearchTable
    showSearch
    endpointParams={endpointParams}
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    containerClass={[
      'custom-theme-table',
    ]}
    filterTypes={[{
      name: 'Event',
      params: [{
        name: 'contenttype',
        value: 'Event',
      }],
    }, {
      name: 'Publication',
      params: [{
        name: 'contenttype',
        value: 'Publication',
      }],
    }, {
      name: 'Multimedia',
      params: [{
        name: 'contenttype',
        value: 'Multimedia',
      }],
    }, {
      name: 'Opinion',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Opinion',
      }],
    }, {
      name: 'Op-Eds',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Op-Eds',
      }],
    }, {
      name: 'CIGI in the News',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'CIGI in the News',
      }],
    }, {
      name: 'News Releases',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'News Releases',
      }],
    }]}
    RowComponent={ProjectContentListing}
    tableColumns={[{
      colSpan: 4,
      colTitle: 'Title',
    }, {
      colSpan: 3,
      colTitle: 'Expert',
    }, {
      colSpan: 2,
      colTitle: 'Topic',
    }, {
      colSpan: 2,
      colTitle: 'Type',
    }, {
      colSpan: 1,
      colTitle: 'PDF',
    }]}
  />,
  document.getElementById('project-search-table'),
);
