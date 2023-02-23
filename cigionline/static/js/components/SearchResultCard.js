import React from 'react';
import PropTypes from 'prop-types';
import ArticleSearchResultCard from './ArticleSearchResultCard';
import MultimediaSearchResultCard from './MultimediaSearchResultCard';
import PublicationSearchResultCard from './PublicationSearchResultCard';
import ArticleSeriesSearchResultCard from './ArticleSeriesSearchResultCard';
import ExpertSearchResultCard from './ExpertSearchResultCard';
import EventSearchResultCard from './EventSearchResultCard';

const SearchResultCard = (props) => {
  const { row } = props;

  return (
    <div className="article-container__border">
      {row.contenttype === 'Multimedia' && (
        <MultimediaSearchResultCard row={row} />
      )}
      {row.contenttype === 'Opinion' && <ArticleSearchResultCard row={row} />}
      {row.contenttype === 'Publication' && (
        <PublicationSearchResultCard row={row} />
      )}
      {row.contenttype === 'Opinion Series' && (
        <ArticleSeriesSearchResultCard row={row} />
      )}
      {row.contenttype === 'Person' && <ExpertSearchResultCard row={row} />}
      {row.contenttype === 'Event' && <EventSearchResultCard row={row} />}
    </div>
  );
};

SearchResultCard.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contenttype: PropTypes.string,
    contentsubtype: PropTypes.string,
    id: PropTypes.number,
    image_hero_url: PropTypes.string,
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    url: PropTypes.string.isRequired,
  }).isRequired,
};

export default SearchResultCard;
