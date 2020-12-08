import React from 'react';
import ReactDOM from 'react-dom';
import MultimediaListing from './js/components/MultimediaListing';
import SearchTable from './js/components/SearchTable';

class MultimediaListing2 extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      multimediaPages: [],
      page: 1,
      totalCount: 0,
    };
  }

  componentDidMount() {
    this.getMultimediaPages();
  }

  setPage(page) {
    this.setState({
      page,
    }, this.getMultimediaPages);
  }

  getMultimediaPages() {
    const { page } = this.state;
    fetch(`/api/multimedia/?limit=18&offset=${((page - 1) * 18)}&fields=title,url,publishing_date,topics(title,url),image_hero_url,speakers`)
      .then((res) => res.json())
      .then((data) => {
        this.setState(() => ({
          multimediaPages: data.items,
          totalCount: data.meta.total_count,
        }));
      });
  }

  get hasPrevPage() {
    const { page } = this.state;
    return page > 1;
  }

  get hasNextPage() {
    const { page } = this.state;
    return this.totalPages > page;
  }

  get pageNumbers() {
    const { page } = this.state;

    const pageNumbers = [page];
    if (page > 1) {
      for (const i of Array(Math.max(2, page - (this.totalPages - 4))).keys()) {
        if (page - (i + 1) >= 1) {
          pageNumbers.push(page - (i + 1));
        }
      }
    }
    if (page < this.totalPages) {
      for (const i of Array(5 - pageNumbers.length).keys()) {
        if (page + (i + 1) <= this.totalPages) {
          pageNumbers.push(page + (i + 1));
        }
      }
    }

    pageNumbers.sort();

    return pageNumbers.map((p) => ({
      current: p === page,
      page: p,
    }));
  }

  get totalPages() {
    const { totalCount } = this.state;
    return Math.ceil(totalCount / 18);
  }

  render() {
    const { multimediaPages } = this.state;
    return (
      <>
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
        <div className="pagination">
          <div className="pagination-links-numbered">
            {this.hasPrevPage && (
              <>
                <li className="pagination-link-first pagination-underline">
                  <a onClick={() => this.setPage(1)}>
                    first page
                  </a>
                </li>
                <li className="pagination-underline pagination-underline-centred">
                  <a onClick={() => this.setPage(page - 1)}>
                    <i className="fa fa-chevron-left" />
                  </a>
                </li>
              </>
            )}
            {this.pageNumbers.map((pageNumber) => (
              pageNumber.current
                ? <li className="active pagination-underline pagination-underline-centred"><span>{pageNumber.page}</span></li>
                : <li><a onClick={() => this.setPage(pageNumber.page)}>{pageNumber.page}</a></li>
            ))}
            {this.hasNextPage && (
              <>
                <li className="pagination-underline pagination-underline-centred">
                  <a onClick={() => this.setPage(page + 1)}>
                    <i className="fa fa-chevron-right" />
                  </a>
                </li>
                <li className="pagination-link-last pagination-underline">
                  <a onClick={() => this.setPage(this.totalPages)}>
                    last page
                  </a>
                </li>
              </>
            )}
          </div>
        </div>
      </>
    );
  }
}

ReactDOM.render(
  <SearchTable endpoint="/multimedia" limit={18} fields="title,url,publishing_date,topics(title,url),image_hero_url,speakers" containerClass={['row', 'row-cols-1', 'row-cols-sm-2', 'row-cols-md-3', 'multimedia-list-row']} RowComponent={MultimediaListing} />,
  document.getElementById('multimedia-listing'),
);
