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
      loadingYears: true,
      loadingTypes: true,
      rows: [],
      searchValue: '',
      sortSelected: null,
      topics: [],
      topicSelectValues: [],
      topicsFilter: '',
      typeSelectValues: [],
      years: [],
      yearSelectValues: [],
      totalRows: 0
    };

    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleSortSelect = this.handleSortSelect.bind(this);
    this.handleTopicSelect = this.handleTopicSelect.bind(this);
    this.handleTypeSelect = this.handleTypeSelect.bind(this);
    this.handleYearSelect = this.handleYearSelect.bind(this);
  }

  componentDidMount() {
    const { filterTypes: propsFilterTypes, isSearchPage, showSearch } = this.props;
    const { filterTypes } = this.state;
    if (isSearchPage) {
      const params = (new URL(window.location)).searchParams;
      const query = params.get('query');
      const sort = params.get('sort');
      const topic = params.getAll('topic').map(t => parseInt(t));
      const type = params.getAll('type');
      const year = params.getAll('year').map(t => parseInt(t));
      const initialState = {};
      if (query) {
        initialState.searchValue = query;
      }
      if (sort) {
        initialState.sortSelected = sort;
      }
      if (topic.length > 0) {
        initialState.topicSelectValues = topic
      }
      if (type.length > 0) {
        initialState.typeSelectValues = type
      }
      if (year.length > 0) {
        initialState.yearSelectValues = year
      }
      this.setState(initialState, this.getRows);
    } else {
      this.getRows();
    }
    if (showSearch) {
      this.getTopics();
      this.getYears();
      this.getTypes();
      // const filterTypeEndpoints = [];
      // for (const filterType of filterTypes) {
      //   if (filterType.typeEndpoint
      //       && filterTypeEndpoints.indexOf(filterType.typeEndpoint) < 0) {
      //     filterTypeEndpoints.push(filterType.typeEndpoint);
      //   }
      // }
      // for (const filterTypeEndpoint of filterTypeEndpoints) {
      //   this.getTypes(filterTypeEndpoint);
      // }
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
    let topics = this.state.topicSelectValues;
    if(e.target.checked){
      topics.push(id);
    } else{
      topics = topics.filter(f => f !== id)
    }
    this.setState({
      topicSelectValues: topics,
    }, this.getRows);
  }

  handleYearSelect(e, year){
    let years = this.state.yearSelectValues;
    if(e.target.checked){
      years.push(year);
    } else{
      years = years.filter(f => f !== year)
    }
    this.setState({
      yearSelectValues: years,
    }, this.getRows);
  }

  handleTypeSelect(e, type, subtype) {
    let types = this.state.typeSelectValues;
    let filtertype = this.props.filterTypes.find(f => f.name === type);
    if(filtertype.subtypes == undefined){
      filtertype.subtypes = []
    }
    // if we are dealing with parent type
    if(subtype === undefined){
      if(e.target.checked){ // if we are adding, we need to add all
        types.push(type);
        filtertype.subtypes.map((s) => {
          types.push(type+"_"+s);
        })
      } else{ // if we are removing we need to remove all
        types = types.filter(f => f !== type)
        filtertype.subtypes.map((s) => {
          types = types.filter(f => f !== type+"_"+s);
        })
      }
    }else{ // if subtype is defined
      if(e.target.checked){ // if we are adding, we need to check if all are added and then add parent
        types.push(type + "_" + subtype);
        let allchecked = filtertype.subtypes.map(f => types.includes(type + "_" + f)).every(Boolean)
        if(allchecked){
          types.push(type)
        }
      }else{ // if we are removing, we need to remove parent
        types = types.filter(f => f !== type+"_"+subtype);
        types = types.filter(f => f !== type);
      }
    }
    
    this.setState({
      typeSelectValues: [...new Set(types)],
    }, this.getRows);
  }

  getRows() {
    const {
      currentPage,
      loadingInitial,
      searchValue,
      sortSelected,
      topicSelectValues,
      yearSelectValues,
      typeSelectValues
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
    if (typeSelectValues.length == 0) {
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
    if (topicSelectValues.length > 0) {
      topicSelectValues.map(t => {
        uri += `&topic=${t}`;
      })
    }
    if (yearSelectValues.length > 0) {
      yearSelectValues.map(t => {
        uri += `&year=${t}`;
      })
    }
    if (typeSelectValues > 0) {
      typeSelectValues.map(t => {
        uri += `&type=${t}`;
      })
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

  getYears() {
    //Here we need to add fetch code for getting the years
    this.setState(() => ({
      loadingYears: false,
      years: Array.from({ length: 12 }, (_, i) => 2021 - i)
    }));
  }

  getTypes() {
    this.setState(() => ({
      loadingTypes: false,
    }));
  }

  setPage(page) {
    this.setState(() => ({
      currentPage: page,
    }), this.getRows);
  }

  get dropdownTopics() {
    const { topics, topicSelectValues } = this.state;
    const dropdownTopics = [];
    topics.forEach((topic) => {
        dropdownTopics.push(topic);
    });
    if (topics.length !== dropdownTopics.length) {
      dropdownTopics.unshift({
        id: null,
        title: 'All Topics',
      });
    }
    return dropdownTopics;
  }

  get dropdownTypes() {
    const { typeSelected } = this.state;
    const { filterTypes } = this.state;
    const dropdownTypes = [];
    filterTypes.forEach((filterType) => {
        dropdownTypes.push(filterType);
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
      topicSelectValues,
      typeSelectValues,
      yearSelectValues,
    } = this.state;
    const url = new URL(window.location);
    url.searchParams.set('query', searchValue);
    if (sortSelected) {
      url.searchParams.set('sort', sortSelected);
    } else {
      url.searchParams.delete('sort');
    }
    if (topicSelectValues.length > 0) {
      url.searchParams.delete('topic');
      topicSelectValues.map(t => {
        url.searchParams.append('topic', t);
      })
    } else {
      url.searchParams.delete('topic');
    }
    if (typeSelectValues.length > 0) {
      url.searchParams.delete('type');
      typeSelectValues.map(t => {
        url.searchParams.append('type', t);
      })
    } else {
      url.searchParams.delete('type');
    }
    if (yearSelectValues.length > 0) {
      url.searchParams.delete('year');
      yearSelectValues.map(t => {
        url.searchParams.append('year', t);
      })
    } else {
      url.searchParams.delete('year');
    }
    window.history.pushState({}, '', url);
  }

  handleTopicsFilter(e) {
    this.setState(() => ({
      topicsFilter: e.target.value
    }))
  }

  render() {
    const {
      currentPage,
      loading,
      loadingInitial,
      loadingTopics,
      loadingYears,
      loadingTypes,
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
      <div className="row">
        <div className="search-filters col-md-3">
          {!hideTopicDropdown && (
            <div className="dropdown custom-dropdown keep-open">
              <button className="dropdown-toggle" type="button" id="search-bar-topics" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Topics
              </button>
              <div className="dropdown-menu show" aria-labelledby="search-bar-topics">
                <div className="topic-filter">
                  <div className="input-group input-group-search">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="search of a topic"
                      onKeyUp={(e) => this.handleTopicsFilter(e)}
                    />
                    <div className="input-group-append">
                      <button className="btn-search" type="submit">
                        <i className="far fa-search" />
                      </button>
                    </div>
                  </div>
                </div>
                {!loadingTopics && (
                  <ul>
                  { this.dropdownTopics.filter(topic => this.state.topicsFilter == "" || topic.title.toLowerCase().includes(this.state.topicsFilter.toLowerCase())).map((topic) => (
                    <li className="dropdown-item" key={`topic-${topic.id}`}>
                      <label className="keep-open">
                        <input type="checkbox"
                          id={`topic-${topic.id}`}
                          checked={this.state.topicSelectValues.includes(topic.id) ? "checked" : ""}
                          onChange={(e) => this.handleTopicSelect(e, topic.id)}
                        />
                        <span></span>
                        {topic.title}
                      </label>
                    </li>
                  ))}
                  </ul>
                )}
              </div>
            </div>
          )}
          {!loadingTypes && (
            <div className="dropdown custom-dropdown">
              <button className="dropdown-toggle" type="button" id="search-bar-types" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Types
              </button>
              <div className="dropdown-menu w-100 show" aria-labelledby="search-bar-types">
                  <ul>
                  {this.dropdownTypes.map(function(type){
                    return (
                    <li className="dropdown-item" key={`type-${type.name.replace(' ', '_')}`}>
                      <label className="keep-open">
                        <input type="checkbox"
                          onChange={(e) => this.handleTypeSelect(e, type.name)}
                          className={`${this.state.typeSelectValues.some(t => t.split("_")[0] === type.name) ? "partial" : ""}`}
                          checked={this.state.typeSelectValues.includes(type.name) ? "checked" : ""}
                        />
                        <span></span>
                        {type.name}
                        </label>
                        { type.subtypes && type.subtypes.length > 0 &&
                        <ul>
                        { type.subtypes.map((subtype) => (
                          <li className="dropdown-item" key={`subtype-${subtype.replace(' ', '_')}`}>
                            <label className="keep-open">
                              <input type="checkbox"
                                  onChange={(e) => this.handleTypeSelect(e, type.name, subtype)}
                                  checked={this.state.typeSelectValues.includes(type.name + "_" + subtype) ? "checked" : ""}
                                  className={`${type.name} ${type.name + "_" + subtype}`}
                              />
                              <span></span>
                              {subtype}
                            </label>
                          </li>
                        ))}
                        </ul>
                        }
                    </li>
                  )}, this)}
                  </ul>
              </div>
            </div>
          )}

          <div className="dropdown custom-dropdown">
            <button className="dropdown-toggle" type="button" id="search-bar-years" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Years
            </button>
            <div className="dropdown-menu show" aria-labelledby="search-bar-years">
              {!loadingYears && (
                <ul className="columns-2">
                { this.state.years.map((year) => (
                  <li className="dropdown-item" key={`year-${year}`}>
                    <label>
                      <input type="checkbox"
                        id={`year-${year}`}
                        checked={this.state.yearSelectValues.includes(year) ? "checked" : ""}
                        onChange={(e) => this.handleYearSelect(e, year)}
                      />
                      <span></span>
                      {year}
                    </label>
                  </li>
                ))}
                </ul>
              )}
            </div>
          </div>
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
