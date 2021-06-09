import PropTypes from 'prop-types';
import React from 'react';

import Paginator from './Paginator';
import SearchTableSkeleton from './SearchTableSkeleton';
import '../../css/components/SearchTable.scss';

class SearchTable extends React.Component {
  constructor(props) {
    super(props);
    this.searchTableRef = React.createRef();
    const { filterTypes } = props;
    this.state = {
      currentPage: 1,
      filterTypes,
      loading: true,
      loadingInitial: true,
      loadingTopics: true,
      rows: [],
      searchValue: '',
      sortSelected: null,
      topics: [],
      topicSelectValue: [],
      typeSelected: null,
      totalRows: 0,
    };

    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleSortSelect = this.handleSortSelect.bind(this);
    this.handleTopicSelect = this.handleTopicSelect.bind(this);
  }

  componentDidMount() {
    const { filterTypes: propsFilterTypes, isSearchPage, showSearch } = this.props;
    const { filterTypes } = this.state;
    if (isSearchPage) {
      const params = (new URL(window.location)).searchParams;
      const query = params.get('query');
      const sort = params.get('sort');
      const topic = params.get('topic');
      const type = params.get('type');
      const initialState = {};
      if (query) {
        initialState.searchValue = query;
      }
      if (sort) {
        initialState.sortSelected = sort;
      }
      if (topic && !isNaN(topic)) {
        initialState.topicSelectValue = topic.split(",").map(t => parseInt(t, 10));
      }
      if (type) {
        for (const filterType of propsFilterTypes) {
          if (type === filterType.name) {
            initialState.typeSelected = filterType;
          }
        }
      }
      this.setState(initialState, this.getRows);
    } else {
      this.getRows();
    }
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
    // When searching, set the page to the first page to display the most
    // relevant results. Note that setPage will also call the API to update the
    // table.
    this.setPage(1);
  }

  handleSearchValueChange(e) {
    this.setState({
      searchValue: e.target.value,
    });
  }

  handleSortSelect(sortValue) {
    this.setState({
      sortSelected: sortValue,
    }, this.getRows);
  }

  handleTopicSelect(e, id) {
    let topics = this.state.topicSelectValue;
    if(e.target.checked){
      topics.push(id);
    }else{
      topics.pop(id);
    }
    this.setState({
      topicSelectValue: topics,
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
      sortSelected,
      topicSelectValue,
      typeSelected,
    } = this.state;
    const {
      contentsubtypes,
      contenttypes,
      endpointParams,
      fields,
      isSearchPage,
      limit,
      sortOptions,
    } = this.props;

    if (isSearchPage) {
      this.updateQueryParams();
    }

    const offset = (currentPage - 1) * limit;

    this.setState(() => ({
      loading: true,
    }));
    if (!loadingInitial) {
      this.searchTableRef.current.scrollIntoView({ behavior: 'smooth' });
    }

    let uri = `/api/search/?limit=${limit}&offset=${offset}`;
    if (sortSelected) {
      uri += `&sort=${sortSelected}`;
    } else {
      for (const sortOption of sortOptions) {
        if (sortOption.default) {
          uri += `&sort=${sortOption.value}`;
        }
      }
    }
    if (!typeSelected) {
      for (const contenttype of contenttypes) {
        uri += `&contenttype=${contenttype}`;
      }
      for (const contentsubtype of contentsubtypes) {
        uri += `&contentsubtype=${contentsubtype}`;
      }
    }
    for (const field of fields) {
      uri += `&field=${field}`;
    }
    for (const endpointParam of endpointParams) {
      uri += `&${endpointParam.paramName}=${endpointParam.paramValue}`;
    }
    if (searchValue) {
      uri += `&searchtext=${searchValue}`;
    }
    if (topicSelectValue.length > 0) {
      topicSelectValue.map(t => {
        uri += `&topic=${t}`;
      })
    }
    if (typeSelected && typeSelected.param) {
      uri += `&${typeSelected.param}=${typeSelected.value}`;
    }
    if (isSearchPage) {
      uri += '&searchpage=true';
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

  updateQueryParams() {
    const {
      searchValue,
      sortSelected,
      topicSelectValue,
      typeSelected,
    } = this.state;
    const url = new URL(window.location);
    url.searchParams.set('query', searchValue);
    if (sortSelected) {
      url.searchParams.set('sort', sortSelected);
    } else {
      url.searchParams.delete('sort');
    }
    if (topicSelectValue.length > 0) {
      topicSelectValue.map(t => {
        url.searchParams.set('topic', t);
      })
    } else {
      url.searchParams.delete('topic');
    }
    if (typeSelected) {
      url.searchParams.set('type', typeSelected.name);
    } else {
      url.searchParams.delete('type');
    }
    window.history.pushState({}, '', url);
  }

  render() {
    const {
      currentPage,
      loading,
      loadingInitial,
      loadingTopics,
      rows,
      searchValue,
      sortSelected,
      totalRows,
    } = this.state;
    const {
      blockListing,
      containerClass,
      filterTypes,
      hideTopicDropdown,
      RowComponent,
      searchPlaceholder,
      showCount,
      showSearch,
      sortOptions,
      tableColumns,
    } = this.props;

    return (
      <div class="row">
        <div className="search-filters col-md-3">
          {!hideTopicDropdown && (
            <div className="dropdown custom-dropdown keep-open">
              <button className="dropdown-toggle" type="button" id="search-bar-topics" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                {this.dropdownSelectedTopic}
              </button>
              <div className="dropdown-menu" aria-labelledby="search-bar-topics">
                {!loadingTopics && (
                  <ul>
                  { this.dropdownTopics.map((topic) => (
                    <li className="dropdown-item">
                      <label className="keep-open">
                        <input type="checkbox"
                          id={`topic-${topic.id}`}
                          key={`topic-${topic.id}`}
                          defaultChecked={topic.id in this.state.topicSelectValue ? "checked" : ""}
                          onClick={(e) => this.handleTopicSelect(e, topic.id)}
                        />
                        {topic.title}
                      </label>
                    </li>
                  ))}
                  </ul>
                )}
              </div>
            </div>
          )}
          {!!filterTypes.length && (
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
          )}
        </div>
        <div className="search-table col-md-9">
          <div ref={this.searchTableRef} className="search-table-scroll" />
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
                </div>
              </form>
              <div className="search-bar-sort-wrapper">
                <span>Sort by:</span>
                <ul className="search-bar-sort-list">
                  {sortOptions.map((sortOption) => (
                    <li key={`sort-${sortOption.value}`}>
                      <button
                        type="button"
                        className={['search-bar-sort-link', (sortSelected === sortOption.value || (!sortSelected && sortOption.default)) && 'active'].join(' ')}
                        onClick={() => this.handleSortSelect(sortOption.value)}
                      >
                        {sortOption.name}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          {loadingInitial
            ? <SearchTableSkeleton />
            : rows.length
              ? (
                <>
                  {showCount && totalRows && (
                    <div className="search-table-count">
                      {`${totalRows} results found.`}
                    </div>
                  )}
                  {blockListing
                    ? (
                      <div className={[...containerClass, 'search-results', loading && 'loading'].join(' ')}>
                        {rows.map((row) => (
                          <RowComponent key={`${row.id}-${row.elevated}`} row={row} />
                        ))}
                      </div>
                    ) : (
                      <table className={[...containerClass, 'search-results', loading && 'loading'].join(' ')}>
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
                            <RowComponent key={`${row.id}-${row.elevated}`} row={row} />
                          ))}
                        </tbody>
                      </table>
                    )}
                </>
              ) : (
                <p>
                  Your query returned no results. Please check your spelling and try again.
                </p>
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
      </div>
    );
  }
}

SearchTable.propTypes = {
  blockListing: PropTypes.bool,
  containerClass: PropTypes.arrayOf(PropTypes.string),
  contentsubtypes: PropTypes.arrayOf(PropTypes.string),
  contenttypes: PropTypes.arrayOf(PropTypes.string),
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
  isSearchPage: PropTypes.bool,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
  searchPlaceholder: PropTypes.string,
  showCount: PropTypes.bool,
  showSearch: PropTypes.bool,
  sortOptions: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    value: PropTypes.string,
  })),
  tableColumns: PropTypes.arrayOf(PropTypes.shape({
    colSpan: PropTypes.number,
    colTitle: PropTypes.string,
  })),
};

SearchTable.defaultProps = {
  blockListing: false,
  containerClass: [],
  contentsubtypes: [],
  contenttypes: [],
  endpointParams: [],
  filterTypes: [],
  hideTopicDropdown: false,
  isSearchPage: false,
  limit: 24,
  searchPlaceholder: 'Search',
  showCount: false,
  showSearch: false,
  sortOptions: [{
    default: true,
    name: 'Date',
    value: 'date',
  }],
  tableColumns: [],
};

export default SearchTable;
