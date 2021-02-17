import PropTypes from 'prop-types';
import React from 'react';

import Paginator from './Paginator';
import PaginatorAlphabetical from './PaginatorAlphabetical';
import SearchTableSkeleton from './SearchTableSkeleton';
import '../../css/components/SearchTable.scss';

class SearchTable extends React.Component {
  constructor(props) {
    super(props);
    this.searchResultsRef = React.createRef();
    const { filterTypes } = props;
    this.state = {
      currentPage: 1,
      currentLetter: 'all',
      filterTypes,
      letters: {},
      loading: true,
      loadingInitial: true,
      loadingTopics: true,
      rows: [],
      searchValue: '',
      topics: [],
      topicSelectValue: null,
      typeSelected: null,
      totalRows: 0,
    };

    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleTopicSelect = this.handleTopicSelect.bind(this);
  }

  componentDidMount() {
    const { showSearch } = this.props;
    const { filterTypes } = this.state;
    this.getRows();
    if (showSearch) {
      this.getTopics();
      const filterTypeEndpoints = [];
      for (const filterType of filterTypes) {
        if (filterType.typeEndpoint
            && filterTypeEndpoints.indexOf(filterType.typeEndpoint) < 0) {
          filterTypeEndpoints.push(filterType.typeEndpoint);
        }
      }
      for (const filterTypeEndpoint of filterTypeEndpoints) {
        this.getTypes(filterTypeEndpoint);
      }
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
    }, this.getRows);
  }

  handleTypeSelect(type) {
    if (type.id || type.value || type.endpoint) {
      this.setState({
        typeSelected: type,
      }, this.getRows);
    } else {
      this.setState({
        typeSelected: null,
      }, this.getRows);
    }
  }

  getRows() {
    const {
      currentPage,
      loadingInitial,
      searchValue,
      topicSelectValue,
      typeSelected,
    } = this.state;
    const {
      contentType,
      contentsubtypes,
      contenttypes,
      paginateAlphabetically,
      persontypes,
      endpointParams,
      fields,
      limit,
    } = this.props;

    const offset = (currentPage - 1) * limit;

    this.setState(() => ({
      loading: true,
    }));
    if (!loadingInitial) {
      this.searchResultsRef.current.scrollIntoView({ behavior: 'smooth' });
    }

    let uri = `/api/search/?limit=${limit}&offset=${offset}`;
    for (const type of contenttypes) {
      uri += `&contenttype=${type}`;
    }
    for (const contentsubtype of contentsubtypes) {
      uri += `&contentsubtype=${contentsubtype}`;
    }
    for (const persontype of persontypes) {
      uri += `&persontype=${persontype}`;
    }
    for (const field of fields) {
      uri += `&field=${field}`;
    }
    for (const endpointParam of endpointParams) {
      uri += `&${endpointParam.paramName}=${endpointParam.paramValue}`;
    }
    if (contentType) {
      uri += `&content_type=${contentType}`;
    }
    if (searchValue) {
      uri += `&searchtext=${searchValue}`;
    }
    if (topicSelectValue) {
      uri += `&topic=${topicSelectValue}`;
    }
    if (typeSelected && typeSelected.param) {
      uri += `&${typeSelected.param}=${typeSelected.value}`;
    }

    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        this.setState({
          loading: false,
          loadingInitial: false,
          rows: data.items,
          totalRows: data.meta.total_count,
        }, () => {
          this.setLetters(paginateAlphabetically);
        });
      });
  }

  getTypes(typeEndpoint) {
    fetch(encodeURI(`/api${typeEndpoint}/?limit=40&offset=0&fields=title`))
      .then((res) => res.json())
      .then((data) => {
        for (const item of data.items) {
          const { filterTypes: existingFilterTypes } = this.state;
          const itemIndex = existingFilterTypes.findIndex(
            (filterType) => (
              filterType.typeEndpoint === typeEndpoint
                && filterType.typeValue === item.title
            ),
          );
          if (itemIndex >= 0) {
            this.setState(({ filterTypes }) => ({
              filterTypes: [
                ...filterTypes.slice(0, itemIndex),
                {
                  ...filterTypes[itemIndex],
                  id: item.id,
                },
                ...filterTypes.slice(itemIndex + 1),
              ],
            }));
          }
        }
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

  setPage(page) {
    this.setState(() => ({
      currentPage: page,
    }), this.getRows);
  }

  setLetters(paginateAlphabetically) {
    if (paginateAlphabetically) {
      const { rows } = this.state;
      const letters = {
        all: rows,
      };
      rows.forEach((row) => {
        const letter = row.last_name[0];
        if (!(letter in letters)) {
          letters[letter] = [];
        }

        letters[letter].push(row);
      });

      this.setState(() => ({
        letters,
      }));
    }
  }

  setLetter(letter) {
    const { letters } = this.state;
    this.setState(() => ({
      currentLetter: letter,
      rows: letters[letter],
    }));
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

  get dropdownSelectedType() {
    const { typeSelected } = this.state;
    if (typeSelected && typeSelected.name) {
      return typeSelected.name;
    }
    return 'All Types';
  }

  get dropdownTypes() {
    const { typeSelected } = this.state;
    const { filterTypes } = this.state;
    const dropdownTypes = [];
    filterTypes.forEach((filterType) => {
      if ((!filterType.typeEndpoint || filterType.id)
          && (!typeSelected
            || (typeSelected
              && typeSelected.name !== filterType.name))) {
        dropdownTypes.push(filterType);
      }
    });
    if (filterTypes.length !== dropdownTypes.length) {
      dropdownTypes.unshift({
        name: 'All Types',
        value: null,
      });
    }
    return dropdownTypes;
  }

  get totalPages() {
    const { limit } = this.props;
    const { totalRows } = this.state;
    return Math.ceil(totalRows / limit);
  }

  render() {
    const {
      currentLetter,
      currentPage,
      letters,
      loading,
      loadingInitial,
      loadingTopics,
      rows,
      searchValue,
    } = this.state;
    const {
      blockListing,
      BlockListingHeading,
      containerClass,
      filterTypes,
      hideTopicDropdown,
      paginateAlphabetically,
      RowComponent,
      searchPlaceholder,
      showSearch,
      tableColumns,
    } = this.props;

    return (
      <div className="search-table">
        {paginateAlphabetically && (
          <PaginatorAlphabetical
            currentLetter={currentLetter}
            setLetter={(letter) => this.setLetter(letter)}
            letters={Object.keys(letters)}
          />
        )}
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
                      placeholder={searchPlaceholder}
                      onChange={this.handleSearchValueChange}
                    />
                    <div className="input-group-append">
                      <button className="btn-search" type="submit">
                        <i className="far fa-search" />
                      </button>
                    </div>
                  </div>
                </div>
                {!hideTopicDropdown && (
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
                )}
                {!!filterTypes.length && (
                  <div className="col-md-3 position-relative">
                    <div className="dropdown custom-dropdown">
                      <button className="dropdown-toggle" type="button" id="search-bar-types" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        {this.dropdownSelectedType}
                      </button>
                      <div className="dropdown-menu w-100" aria-labelledby="search-bar-types">
                        {this.dropdownTypes.map((type) => (
                          <button
                            key={`type-${type.name.replace(' ', '_')}`}
                            className="dropdown-item"
                            type="button"
                            onClick={() => this.handleTypeSelect(type)}
                          >
                            {type.name}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </form>
            <div className="search-bar-sort-wrapper">
              <span>Sort by:</span>
              <ul className="search-bar-sort-list">
                <li>
                  <button type="button" className="search-bar-sort-link active">
                    Date
                  </button>
                </li>
              </ul>
            </div>
          </div>
        )}
        {loadingInitial
          ? <SearchTableSkeleton />
          : rows.length
            ? (
              blockListing
                ? (
                  <div ref={this.searchResultsRef} className={[...containerClass, 'search-results', loading && 'loading'].join(' ')}>
                    {BlockListingHeading && <BlockListingHeading />}
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
                )
            ) : (
              <p ref={this.searchResultsRef}>
                Your query returned no results. Please check your spelling and try again.
              </p>
            )}
        {!paginateAlphabetically && (
          <Paginator
            currentPage={currentPage}
            totalPages={this.totalPages}
            setPage={(page) => this.setPage(page)}
          />
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

SearchTable.propTypes = {
  blockListing: PropTypes.bool,
  BlockListingHeading: PropTypes.func,
  containerClass: PropTypes.arrayOf(PropTypes.string),
  contentType: PropTypes.string,
  contentsubtypes: PropTypes.arrayOf(PropTypes.string),
  contenttypes: PropTypes.arrayOf(PropTypes.string),
  persontypes: PropTypes.arrayOf(PropTypes.string),
  endpointParams: PropTypes.arrayOf(PropTypes.shape({
    paramName: PropTypes.string,
    paramValue: PropTypes.any,
  })),
  fields: PropTypes.arrayOf(PropTypes.string).isRequired,
  filterTypes: PropTypes.arrayOf(PropTypes.shape({
    endpoint: PropTypes.string,
    name: PropTypes.string,
    param: PropTypes.string,
    value: PropTypes.string,
  })),
  hideTopicDropdown: PropTypes.bool,
  limit: PropTypes.number,
  paginateAlphabetically: PropTypes.bool,
  RowComponent: PropTypes.func.isRequired,
  searchPlaceholder: PropTypes.string,
  showSearch: PropTypes.bool,
  tableColumns: PropTypes.arrayOf(PropTypes.shape({
    colSpan: PropTypes.number,
    colTitle: PropTypes.string,
  })),
};

SearchTable.defaultProps = {
  blockListing: false,
  BlockListingHeading: null,
  containerClass: [],
  contentType: '',
  contentsubtypes: [],
  contenttypes: [],
  persontypes: [],
  endpointParams: [],
  filterTypes: [],
  hideTopicDropdown: false,
  limit: 24,
  paginateAlphabetically: false,
  searchPlaceholder: 'Search',
  showSearch: false,
  tableColumns: [],
};

export default SearchTable;
