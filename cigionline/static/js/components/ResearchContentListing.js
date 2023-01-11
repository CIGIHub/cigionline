import { DateTime } from 'luxon';
import PropTypes from 'prop-types';
import React from 'react';

function ResearchContentListing(props) {
  const { row } = props;

  return (
    // <tr>
    //   <td colSpan="4">
    //     <div className="table-mobile-text">
    //       Title
    //     </div>
    //     <div className="table-infos-wrapper">
    //       {row.contenttype === 'Event' && (
    //         <span className="table-icon icon-event">
    //           <i className="fal fa-calendar-alt" />
    //         </span>
    //       )}
    //       {row.contenttype === 'Multimedia' && row.contentsubtype === 'Video' && (
    //         <span className="table-icon icon-multimedia">
    //           <i className="fal fa-play" />
    //         </span>
    //       )}
    //       {row.contenttype === 'Multimedia' && row.contentsubtype === 'Audio' && (
    //         <span className="table-icon icon-multimedia">
    //           <i className="fal fa-headphones" />
    //         </span>
    //       )}
    //       {row.contenttype === 'Publication' && (
    //         <span className="table-icon icon-publication">
    //           <i className="fal fa-file-alt" />
    //         </span>
    //       )}
    //       {row.contenttype === 'Opinion' && ['Opinion', 'Interviews', 'Op-Eds'].includes(row.contentsubtype) && (
    //         <span className="table-icon icon-opinion">
    //           <i className="fal fa-comment-dots" />
    //         </span>
    //       )}
    //       {row.contenttype === 'Opinion' && ['CIGI in the News', 'News Releases'].includes(row.contentsubtype) && (
    //         <span className="table-icon icon-media">
    //           <i className="fal fa-bullhorn" />
    //         </span>
    //       )}
    //       {row.contenttype === 'Activity' && (
    //         <span className="table-icon icon-activity">
    //           <i className="fal fa-file-search" />
    //         </span>
    //       )}
    //       <div className="table-infos">
    //         <a href={row.url} className="table-title-link">
    //           {row.title}
    //         </a>
    //         {row.publishing_date && (
    //           <div className="table-infos-meta">
    //             {DateTime.fromISO(row.publishing_date).toLocaleString(DateTime.DATE_FULL)}
    //           </div>
    //         )}
    //       </div>
    //     </div>
    //   </td>
    //   <td colSpan="3">
    //     <div className="table-mobile-text">
    //       Expert
    //     </div>
    //     <div className="table-content">
    //       <ul className="custom-text-list author-list">
    //         {row.authors.map((author) => (
    //           <li key={`${row.id}-author-${author.id}`}>
    //             <a href={author.url} className="table-content-link table-content-link-black">
    //               {author.title}
    //             </a>
    //           </li>
    //         ))}
    //       </ul>
    //     </div>
    //   </td>
    //   <td colSpan="2">
    //     <div className="table-mobile-text">
    //       Topic
    //     </div>
    //     <div className="table-content">
    //       <ul className="custom-text-list">
    //         {row.topics && row.topics.map((topic) => (
    //           <li key={`${row.id}-topic-${topic.id}`}>
    //             <a href={topic.url} className="table-content-link">
    //               {topic.title}
    //             </a>
    //           </li>
    //         ))}
    //       </ul>
    //     </div>
    //   </td>
    //   <td colSpan="2">
    //     <div className="table-mobile-text">
    //       Type
    //     </div>
    //     <div className="table-content">
    //       <ul className="custom-text-list">
    //         <li key={`${row.id}-contenttype`} className="table-infos-meta">
    //           {row.contenttype === 'Opinion' ? row.contentsubtype : row.contenttype}
    //         </li>
    //       </ul>
    //     </div>
    //   </td>
    //   <td colSpan="1">
    //     <div className="table-mobile-text">
    //       PDF
    //     </div>
    //     <div className="table-content">
    //       {row.pdf_download && (
    //         <a href={row.pdf_download} className="table-btn-icon">
    //           <i className="fa fas fa-download" />
    //         </a>
    //       )}
    //     </div>
    //   </td>
    // </tr>
    <article className="card__container card--small card--small--poster">
      <div className="card__image">
        <a href={row.url} className="feature-content-image">
          <div className="img-wrapper">
            <img alt={row.image_alt} src={row.image_poster_url} />
          </div>
        </a>
      </div>
      <div className="card__text">
        <h3 className="card__text__title {{ additional_classes }}">
          <a href={row.url}>{row.title}</a>
        </h3>
        <div className="card__text__meta">
          <div>
            <ul className="custom-text-list card__text__people">
              {row.authors.map((author) => (
                <li key={`${row.id}-author-${author.id}`}>
                  <a href={author.url}>{author.title}</a>
                </li>
              ))}
            </ul>
            <ul className="card__text__topics custom-text-list {{ additional_class_names }} {% if topics|length > 2 %}hide-topics{% endif %}">
              {row.topics &&
                row.topics.map((topic) => (
                  <li key={`${row.id}-topic-${topic.id}`}>
                    <a href={topic.url}>{topic.title}</a>
                  </li>
                ))}
            </ul>
          </div>
          <button type="button" className="card__text__more">
            <a href="{{ url }}">
              <i className="far fa-ellipsis-h" />
            </a>
          </button>
        </div>
      </div>
    </article>
  );
}

ResearchContentListing.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        type: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contentsubtype: PropTypes.string,
    contenttype: PropTypes.string,
    id: PropTypes.number,
    pdf_download: PropTypes.string,
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
    image_poster_url: PropTypes.string,
    image_alt: PropTypes.string,
  }).isRequired,
};

export default ResearchContentListing;
