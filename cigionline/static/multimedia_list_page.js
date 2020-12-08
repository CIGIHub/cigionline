import { DateTime } from 'luxon';
import React from 'react';
import ReactDOM from 'react-dom';

class MultimediaListing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      multimediaPages: [],
    };
  }

  componentDidMount() {
    fetch('/api/multimedia/?limit=18&fields=title,url,publishing_date,topics(title,url),image_hero_url,speakers')
      .then((res) => res.json())
      .then((data) => data.items)
      .then((multimediaPages) => {
        this.setState(() => ({
          multimediaPages,
        }));
      });
  }

  render() {
    const { multimediaPages } = this.state;
    return (
      <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 multimedia-list-row">
        {multimediaPages.map((multimediaPage) => (
          <div key={multimediaPage.id} id={multimediaPage.id} className="col multimedia-list-col">
            <div className="multimedia-card-wrapper">
              <a href={multimediaPage.url} className="multimedia-card-image">
                <div className="img-wrapper" style={{ backgroundImage: `url(${multimediaPage.image_hero_url})` }} />
                <div className="multimedia-image-type">
                  <i className="fas fa-play" />
                </div>
              </a>
              <ul className="custom-text-list multimedia-card-topic-list">
                {multimediaPage.topics.map((topic) => (
                  <li key={topic.id}>
                    <a href={topic.url} className="table-content-link">
                      {topic.title}
                    </a>
                  </li>
                ))}
              </ul>
              <p className="multimedia-card-title">
                <a href={multimediaPage.url}>
                  {multimediaPage.title}
                </a>
              </p>
              <ul className="custom-text-list multimedia-card-speakers-list">
                {multimediaPage.speakers.slice(0, 3).map((speaker) => (
                  <li key={speaker.id}>
                    {speaker.type === 'speaker' && (
                      <a href={speaker.value.url}>
                        {speaker.value.title}
                      </a>
                    )}
                  </li>
                ))}
                {multimediaPage.speakers.length > 3 && (
                  <li key="more">And more</li>
                )}
              </ul>
              <p className="multimedia-card-date">
                {DateTime.fromISO(
                  multimediaPage.publishing_date,
                ).toLocaleString(DateTime.DATE_FULL)}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  }
}

ReactDOM.render(
  <MultimediaListing />,
  document.getElementById('multimedia-listing'),
);
