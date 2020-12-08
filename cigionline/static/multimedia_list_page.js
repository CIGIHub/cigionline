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
    fetch('/api/multimedia')
      .then((res) => res.json())
      .then((data) => data.results)
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
          <div className="col multimedia-list-col" key={multimediaPage.id}>
            <div className="multimedia-card-wrapper">
              <a href={multimediaPage.url} className="multimedia-card-image">
                <div className="img-wrapper" style={{ backgroundImage: `url(${multimediaPage.image_hero_url})` }} />
                <div className="multimedia-image-type">
                  <i className="fas fa-play" />
                </div>
              </a>
              <p className="multimedia-card-title">
                <a href={multimediaPage.url}>
                  {multimediaPage.title}
                </a>
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
