import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';
import CardTextMore from './CardTextMore';

import '../../css/components/ExpertContentListing.scss';

function ExpertContentListing(props) {
  const { row } = props;

  return (
    <tr>
      <td className="search-table__results__row__title">
        <div className="table-mobile-text search-table__results__row__title--mobile">
          Title
        </div>
        <div className="table-infos-wrapper">
          {row.contenttype === 'Event' && (
            <span className="table-icon icon-event">
              <i className="fal fa-calendar-alt" />
            </span>
          )}
          {row.contenttype === 'Multimedia' && row.contentsubtype === 'Video' && (
            <span className="table-icon icon-multimedia">
              <i className="fal fa-play" />
            </span>
          )}
          {row.contenttype === 'Multimedia' && row.contentsubtype === 'Audio' && (
            <span className="table-icon icon-multimedia">
              <i className="fal fa-headphones" />
            </span>
          )}
          {row.contenttype === 'Publication' && (
            <span className="table-icon icon-publication">
              <i className="fal fa-file-alt" />
            </span>
          )}
          {row.contenttype === 'Opinion' && ['Opinion', 'Interviews', 'Op-Eds'].includes(row.contentsubtype) && (
            <span className="table-icon icon-opinion">
              <i className="fal fa-comment-alt-lines" />
            </span>
          )}
          {row.contenttype === 'Opinion' && ['CIGI in the News', 'News Releases'].includes(row.contentsubtype) && (
            <span className="table-icon icon-media">
              <i className="fal fa-bullhorn" />
            </span>
          )}
          <div className="table-infos">
            <a href={row.url} className="table-title-link">
              {row.title}
            </a>
            {row.publishing_date && (
              <div className="table-infos-meta">
                {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
              </div>
            )}
          </div>
        </div>
      </td>
      <td className="search-table__results__row__topics">
        <div className="table-mobile-text">
          Topic
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            {row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </td>
      <td className="search-table__results__row__content-type">
        <div className="table-mobile-text">
          Type
        </div>
        <div className="table-content">
          <ul className="custom-text-list">
            <li key={`${row.id}-contenttype`} className="table-infos-meta">
              {row.contenttype === 'Opinion'
                ? row.contentsubtype
                : row.contenttype}
            </li>
          </ul>
        </div>
      </td>
      <td className="search-table__results__row__more">
        <div className="table-mobile-text">
          {' '}
        </div>
        <CardTextMore
          title={row.title}
          type={row.contenttype}
          url={row.url}
          pdfDownload={row.pdf_download}
        />
      </td>
    </tr>
  );
}

ExpertContentListing.propTypes = {
  row: PropTypes.shape({
    contentsubtype: PropTypes.string,
    contenttype: PropTypes.string,
    id: PropTypes.number,
    pdf_download: PropTypes.string,
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number,
      title: PropTypes.string,
      url: PropTypes.string,
    })),
    url: PropTypes.string.isRequired,
  }).isRequired,
};

export default ExpertContentListing;
