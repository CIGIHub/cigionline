import PropTypes from 'prop-types';
import React, { useState } from 'react';
import CardTextMore from './CardTextMore';

const embedUrl = (str) => {
  if (str) {
    if (str.substr(-1) === '/') {
      str = str.substr(0, str.length - 1);
    }
    const splitArr = str.split('/');
    return 'https://player.vimeo.com/video/'.concat(
      splitArr[splitArr.length - 2],
      '?h=',
      splitArr[splitArr.length - 1],
      '&app_id=122963',
    );
  }
  return '';
};
function MultimediaCardXLarge(props) {
  const [imgHidden, setImgHidden] = useState(false);
  const { row } = props;
  const vimeoUrl = imgHidden
    ? `${embedUrl(row.vimeo_url)}&autoplay=1`
    : embedUrl(row.vimeo_url);
  const multimediaTypeIconCls =
    row.contentsubtype === 'Video'
      ? 'fas fa-play'
      : 'fal fa-microphone icon-audio';
  const handleClick = () => {
    setImgHidden(true);
  };

  return (
    <article
      className={`card__container card--multimedia card--xlarge card--xlarge--multimedia card--multimedia--${
        row.contentsubtype
      } ${row.vimeo_url && 'has-vimeo'}`}
    >
      <div className="card__image">
        <div className="img-wrapper">
          {row.image_url && (
            <img
              className={`${imgHidden && 'hidden'}`}
              alt=""
              src={row.image_url}
            />
          )}
          {row.contentsubtype === 'Video' && row.vimeo_url && (
            <iframe
              title={row.title}
              src={vimeoUrl}
              allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            />
          )}
        </div>
        {row.multimedia_length && (
          <div className={`card__image__mm-length ${imgHidden && 'hidden'}`}>
            {row.multimedia_length}
          </div>
        )}
      </div>
      <div className={`card__text ${imgHidden && 'hidden'}`}>
        <div
          className={`card__text__play-icon ${imgHidden && 'hidden'}`}
          role="button"
          tabIndex={0}
          onClick={() => handleClick()}
          onKeyDown={() => handleClick()}
        >
          <i className={multimediaTypeIconCls} />
        </div>
        {row.topics && (
          <ul className="card__text__topics custom-text-list">
            {row.topics.map((topic) => (
              <li key={`${row.id}-topic-${topic.id}`}>
                <a href={topic.url} className="table-content-link">
                  {topic.title}
                </a>
              </li>
            ))}
          </ul>
        )}
        <h3 className="card__text__title">
          <a href={row.url}>{row.title}</a>
        </h3>
        {row.subtitle && (
          <div
            className="card__text__description"
            dangerouslySetInnerHTML={{ __html: row.subtitle }}
          />
        )}
        <div className="card__text__meta">
          <div>
            <ul className="custom-text-list card__text__people">
              {row.authors.slice(0, 3).map((author) => (
                <li key={`${row.id}-author-${author.id}`}>
                  <a href={author.url}>{author.title}</a>
                </li>
              ))}
              {row.authors.length > 3 && (
                <li key={`${row.id}-author-more`}>and more</li>
              )}
            </ul>
          </div>
          <CardTextMore title={row.title} url={row.url} type="Multimedia" />
        </div>
      </div>
    </article>
  );
}

MultimediaCardXLarge.propTypes = {
  row: PropTypes.shape({
    authors: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        value: PropTypes.any,
      }),
    ),
    contentsubtype: PropTypes.string,
    id: PropTypes.number,
    image_url: PropTypes.string,
    publishing_date: PropTypes.string,
    title: PropTypes.string.isRequired,
    subtitle: PropTypes.string,
    topics: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        title: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    multimedia_length: PropTypes.string,
    url: PropTypes.string.isRequired,
    vimeo_url: PropTypes.string,
  }).isRequired,
};

export default MultimediaCardXLarge;