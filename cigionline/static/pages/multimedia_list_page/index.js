import React from 'react';
import ReactDOM from 'react-dom';
import SearchTableBlockListing from '../../js/components/SearchTableBlockListing';
import './css/multimedia_list_page.scss';
import 'swiper/swiper-bundle.css';
import MultimediaSearchResultCard from '../../js/components/MultimediaSearchResultCard';
import MultimediaCardLarge from '../../js/components/MultimediaCardLarge';

const featuredPage = JSON.parse(document.getElementById('multimedia-search-table').dataset.featuredPage);
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
      'g-4',
    ]}
    columnClass={[
      'col',
      'col-6',
      'col-md-4',
    ]}
    RowComponent={MultimediaSearchResultCard}
    FeaturedItemComponent={MultimediaCardLarge}
    searchPlaceholder="Search Multimedia by Keyword"
    featuredPage={featuredPage}
  />,
  document.getElementById('multimedia-search-table'),
);
