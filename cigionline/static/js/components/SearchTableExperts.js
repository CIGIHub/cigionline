import React from 'react';

import ExpertListing from './ExpertListing';
import SearchTableSkeleton from './SearchTableSkeleton';
import '../../css/components/SearchTable.scss';

class SearchTableExperts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      loadingInitial: true,
      loadingTopics: true,
      rows: [],
      searchValue: '',
      topics: [],
      topicSelectValue: null,
    };

    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleTopicSelect = this.handleTopicSelect.bind(this);
  }

  componentDidMount() {
    this.getRows();
    this.getTopics();
  }

  handleSearchSubmit(e) {
    e.preventDefault();
    this.getRows();
  }

  handleSearchValueChange(e) {
    this.setState({
      searchValue: e.target.value,
    });
  }

  handleTopicSelect(id) {
    this.setState({
      topicSelectValue: id,
    }, this.getRows);
  }

  getRows() {
    const {
      searchValue,
      topicSelectValue,
    } = this.state;

    this.setState(() => ({
      loading: true,
    }));

    let uri = '/api/experts/?limit=150';
    if (searchValue) {
      uri += `&search=${searchValue}`;
    }
    if (topicSelectValue) {
      uri += `&topic=${topicSelectValue}`;
    }

    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        this.setState(() => ({
          loading: false,
          loadingInitial: false,
          rows: data.items,
        }));
      });
  }

  getTopics() {
    fetch(encodeURI('/api/topics/'))
      .then((res) => res.json())
      .then((data) => {
        this.setState(() => ({
          loadingTopics: false,
          topics: data.items.map((topic) => ({
            id: topic.id,
            title: topic.title,
          })),
        }));
      });
  }

  get dropdownSelectedTopic() {
    const { topics, topicSelectValue } = this.state;
    let selectedTopic = 'All Topics';
    topics.forEach((topic) => {
      if (topic.id === topicSelectValue) {
        selectedTopic = topic.title;
      }
    });
    return selectedTopic;
  }

  get dropdownTopics() {
    const { topics, topicSelectValue } = this.state;
    const dropdownTopics = [];
    topics.forEach((topic) => {
      if (topic.id !== topicSelectValue) {
        dropdownTopics.push(topic);
      }
    });
    if (topics.length !== dropdownTopics.length) {
      dropdownTopics.unshift({
        id: null,
        title: 'All Topics',
      });
    }
    return dropdownTopics;
  }

  render() {
    const {
      loading,
      loadingInitial,
      loadingTopics,
      rows,
      searchValue,
    } = this.state;

    return (
      <div className="search-table">
        <div className="search-bar">
          <form className="search-bar-form" onSubmit={this.handleSearchSubmit}>
            <div className="form-row position-relative">
              <div className="col">
                <div className="input-group input-group-search">
                  <input
                    type="text"
                    className="form-control"
                    value={searchValue}
                    placeholder="Search Experts"
                    onChange={this.handleSearchValueChange}
                  />
                  <div className="input-group-append">
                    <button className="btn-search" type="submit">
                      <i className="far fa-search" />
                    </button>
                  </div>
                </div>
              </div>
              <div className="col-md-3 position-static">
                <div className="dropdown custom-dropdown dropdown-full-width">
                  <button className="dropdown-toggle" type="button" id="search-bar-topics" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    {this.dropdownSelectedTopic}
                  </button>
                  <div className="dropdown-menu" aria-labelledby="search-bar-topics">
                    {!loadingTopics && (
                      this.dropdownTopics.map((topic) => (
                        <button
                          key={`topic-${topic.id}`}
                          className="dropdown-item"
                          type="button"
                          onClick={() => this.handleTopicSelect(topic.id)}
                        >
                          {topic.title}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
        {loadingInitial
          ? <SearchTableSkeleton />
          : rows.length
            ? (
              <table className={['custom-theme-table', 'table-experts', 'search-results', loading && 'loading'].join(' ')}>
                <thead>
                  <tr>
                    <th colSpan="3">Name</th>
                    <th colSpan="4">Expertise</th>
                    <th colSpan="4">Recent activity</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <ExpertListing key={row.id} row={row} />
                  ))}
                </tbody>
              </table>
            ) : (
              <p>
                Your query returned no results. Please check your spelling and try again.
              </p>
            )}
        {loading && (
          <img
            src="/static/assets/loader_spinner.gif"
            alt="Loading..."
            className="loading-spinner"
          />
        )}
      </div>
    );
  }
}
export default SearchTableExperts;
