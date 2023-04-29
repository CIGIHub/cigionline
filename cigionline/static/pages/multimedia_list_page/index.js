import React from 'react';
import ReactDOM from 'react-dom';
import Swiper, { Navigation, Pagination } from 'swiper';
import SearchTableBlockListing from '../../js/components/SearchTableBlockListing';
import './css/multimedia_list_page.scss';
import 'swiper/swiper-bundle.css';
import MultimediaSearchResultCard from '../../js/components/MultimediaSearchResultCard';

const submenuItems = document.querySelectorAll('.header--submenu__right__menu-item');
const swipers = {
  'swiper--featured': document.getElementById('swiper--featured'),
  'swiper--big-tech': document.getElementById('swiper--big-tech'),
};
submenuItems.forEach((item) => {
  item.addEventListener('click', (e) => {
    const swiperId = e.target.getAttribute('data-swiper-id');
    submenuItems.forEach((b) => {
      const swiperIdInner = b.getAttribute('data-swiper-id');
      b.classList.remove('active');
      swipers[swiperIdInner].classList.add('hidden');
    });
    e.target.classList.add('active');
    swipers[swiperId].classList.remove('hidden');
  });
});

Swiper.use([Navigation, Pagination]);
const swiperContainerFeatured = document.querySelector('.swiper-container--featured');
const swiperContainerBigTech = document.querySelector('.swiper-container--big-tech');

if (swiperContainerFeatured) {
  const featuredSwiper = new Swiper('.swiper-container--featured', {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next-featured',
      prevEl: '.swiper-button-prev-featured',
    },

    pagination: {
      el: '.swiper-pagination-featured',
      clickable: true,
    },
  });
}

if (swiperContainerBigTech) {
  const bigTechSwiper = new Swiper('.swiper-container--big-tech', {
    slidesPerView: 1,
    slidesPerGroup: 1,
    spaceBetween: 20,
    speed: 800,
    autoHeight: true,
    grabCursor: true,

    navigation: {
      nextEl: '.swiper-button-next-big-tech',
      prevEl: '.swiper-button-prev-big-tech',
    },

    pagination: {
      el: '.swiper-pagination-big-tech',
      clickable: true,
    },
  });
}

ReactDOM.render(
  <SearchTableBlockListing
    blockListing
    contenttypes={[
      'Multimedia',
    ]}
    showSearch
    limit={18}
    fields={[
      'authors',
      'contentsubtype',
      'image_hero_wide_url',
      'publishing_date',
      'topics',
      'multimedia_length',
      'vimeo_url',
    ]}
    filterTypes={[{
      name: 'Video',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Video',
      }],
    }, {
      name: 'Audio',
      aggregationField: 'contentsubtypes',
      params: [{
        name: 'contentsubtype',
        value: 'Audio',
      }],
    }]}
    containerClass={[
      'row',
      'row-cols-2',
      'row-cols-md-3',
      'row-cols-lg-4',
      'g-3',
    ]}
    RowComponent={MultimediaSearchResultCard}
    searchPlaceholder="Search Multimedia by Keyword"
  />,
  document.getElementById('multimedia-search-table'),
);
