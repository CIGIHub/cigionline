import PropTypes from 'prop-types';
import React from 'react';

import Paginator from './Paginator';
import SearchTableSkeleton from './SearchTableSkeleton';
import '../../css/components/SearchTable.scss';

class SearchTable extends React.Component {
  constructor(props) {
    super(props);
    this.searchResultsRef = React.createRef();
    this.state = {
      currentPage: 1,
      loading: true,
      loadingInitial: true,
      loadingTopics: true,
      rows: [],
      searchValue: '',
      topics: [],
      topicSelectValue: null,
      totalRows: 0,
    };

    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleTopicSelect = this.handleTopicSelect.bind(this);
  }

  componentDidMount() {
    const { showSearch } = this.props;
    this.getRows();
    if (showSearch) {
      this.getTopics();
    }
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
    }, () => {
      this.getRows();
    });
  }

  getRows() {
    const {
      currentPage,
      loadingInitial,
      searchValue,
      topicSelectValue,
    } = this.state;
    const { endpoint, fields, limit } = this.props;

    const offset = (currentPage - 1) * limit;

    this.setState(() => ({
      loading: true,
    }));
    if (!loadingInitial) {
      this.searchResultsRef.current.scrollIntoView({ behavior: 'smooth' });
    }

    let uri = `/api${endpoint}/?limit=${limit}&offset=${offset}&fields=${fields}`;
    if (searchValue) {
      uri += `&search=${searchValue}`;
    }
    if (topicSelectValue) {
      uri += `&topics=${topicSelectValue}`;
    }

    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        this.setState(() => ({
          loading: false,
          loadingInitial: false,
          rows: data.items,
          totalRows: data.meta.total_count,
        }));
      });
  }

  getTopics() {
    fetch(encodeURI('/api/topics/?limit=50&offset=0&fields=title'))
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

  setPage(page) {
    this.setState(() => ({
      currentPage: page,
    }), this.getRows);
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

  get totalPages() {
    const { limit } = this.props;
    const { totalRows } = this.state;
    return Math.ceil(totalRows / limit);
  }

  render() {
    const {
      currentPage,
      loading,
      loadingInitial,
      loadingTopics,
      rows,
      searchValue,
    } = this.state;
    const {
      blockListing,
      containerClass,
      RowComponent,
      showSearch,
      tableColumns,
    } = this.props;

    return (
      <div className="search-table">
        {showSearch && (
          <div className="search-bar">
            <form className="search-bar-form" onSubmit={this.handleSearchSubmit}>
              <div className="form-row position-relative">
                <div className="col">
                  <div className="input-group input-group-search">
                    <input
                      type="text"
                      className="form-control"
                      value={searchValue}
                      placeholder="Search"
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
        )}
        {loadingInitial
          ? <SearchTableSkeleton />
          : blockListing
            ? (
              <div ref={this.searchResultsRef} className={[...containerClass, 'search-results', loading && 'loading'].join(' ')}>
                {rows.map((row) => (
                  <RowComponent key={row.id} row={row} />
                ))}
              </div>
            ) : (
              <table ref={this.searchResultsRef} className={[...containerClass, 'search-results', loading && 'loading'].join(' ')}>
                <thead>
                  <tr>
                    {tableColumns.map((tableColumn) => (
                      <th colSpan={tableColumn.colSpan} key={tableColumn.colTitle}>
                        {tableColumn.colTitle}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <RowComponent key={row.id} row={row} />
                  ))}
                </tbody>
              </table>
            )}
        <Paginator
          currentPage={currentPage}
          totalPages={this.totalPages}
          setPage={(page) => this.setPage(page)}
        />
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

SearchTable.propTypes = {
  blockListing: PropTypes.bool,
  containerClass: PropTypes.arrayOf(PropTypes.string).isRequired,
  endpoint: PropTypes.string.isRequired,
  fields: PropTypes.arrayOf(PropTypes.string).isRequired,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
  showSearch: PropTypes.bool,
  tableColumns: PropTypes.arrayOf(PropTypes.shape({
    colSpan: PropTypes.number,
    colTitle: PropTypes.string,
  })),
};

SearchTable.defaultProps = {
  blockListing: false,
  limit: 24,
  showSearch: false,
  tableColumns: [],
};

export default SearchTable;
