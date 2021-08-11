import PropTypes from 'prop-types';
import React from 'react';

import Paginator from './Paginator';
import SearchTableSkeleton from './SearchTableSkeleton';
import '../../css/components/SearchTable.scss';

const mergeObjects = (data) => {
  const result = {};
  data.forEach((obj) => {
    for (const [key, value] of Object.entries(obj)) {
      if (result[key]) {
        result[key] += value;
      } else {
        result[key] = value;
      }
    }
  });
  return result;
};
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
      totalRows: 0,
      aggregations: {
        years: {},
        topics: {},
        contenttypes: {},
        contentsubtypes: {},
        content_types: {},
        event_access: {},
      },
    };

    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleSortSelect = this.handleSortSelect.bind(this);
    this.handleTopicSelect = this.handleTopicSelect.bind(this);
    this.handleTypeSelect = this.handleTypeSelect.bind(this);
    this.handleYearSelect = this.handleYearSelect.bind(this);
    this.removeAllFilters = this.removeAllFilters.bind(this);
    this.getSubTypes = this.getSubTypes.bind(this);
  }

  componentDidMount() {
    const { filterTypes: isSearchPage, showSidebar } = this.props;
    if (isSearchPage) {
      const params = new URL(window.location).searchParams;
      const query = params.get('query');
      const sort = params.get('sort');
      const topic = params.getAll('topic').map((t) => parseInt(t, 10));
      const type = params.getAll('contenttype');
      const subtype = params.getAll('contentsubtype');
      const year = params.getAll('year').map((t) => parseInt(t, 10));
      const initialState = {};
      if (query) {
        initialState.searchValue = query;
      }
      if (sort) {
        initialState.sortSelected = sort;
      }
      if (topic.length > 0) {
        initialState.topicSelectValues = topic;
      }
      if (type.length > 0) {
        initialState.typeSelectValues = type;
      } else {
        initialState.typeSelectValues = [];
      }
      if (subtype.length > 0) {
        initialState.typeSelectValues = initialState.typeSelectValues.concat(subtype);
      }
      if (year.length > 0) {
        initialState.yearSelectValues = year;
      }
      this.setState(initialState, this.getRows);
    } else {
      this.getRows();
    }
    if (showSidebar) {
      this.getTopics();
      this.getYears();
      this.getTypes();
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
    this.setState(
      {
        sortSelected: sortValue,
      },
      this.getRows,
    );
  }

  handleTopicSelect(e, id, checkOverride) {
    const { topicSelectValues } = this.state;
    let topics = topicSelectValues;
    if (e.target.checked || checkOverride) {
      topics.push(id);
    } else {
      topics = topics.filter((f) => f !== id);
    }
    this.setState(
      {
        topicSelectValues: topics,
      },
      this.getRows,
    );
  }

  handleYearSelect(e, year, checkOverride) {
    const { yearSelectValues } = this.state;
    let years = yearSelectValues;
    if (e.target.checked || checkOverride) {
      years.push(year);
    } else {
      years = years.filter((f) => f !== year);
    }
    this.setState(
      {
        yearSelectValues: years,
      },
      this.getRows,
    );
  }

  handleTypeSelect(e, type, subtype, checkOverride) {
    const { typeSelectValues } = this.state;
    let types = typeSelectValues;

    if (e.target.checked || checkOverride) {
      // if we are adding, we need to add all
      types.push(type);
      this.getSubTypes(type).map((s) => {
        types.push(s.name);
        return true;
      });
    } else {
      // if we are removing we need to remove all
      types = types.filter((f) => f !== type);
      this.getSubTypes(type).map((s) => {
        types = types.filter((f) => f !== s.name);
        return true;
      });
    }

    this.setState(
      {
        typeSelectValues: [...new Set(types)],
      },
      this.getRows,
    );
  }

  handleTopicsFilter(e) {
    this.setState(() => ({
      topicsFilter: e.target.value,
    }));
  }

  getRows() {
    const {
      currentPage,
      loadingInitial,
      searchValue,
      sortSelected,
      topicSelectValues,
      yearSelectValues,
      typeSelectValues,
    } = this.state;
    const {
      contentsubtypes,
      contenttypes,
      endpointParams,
      fields,
      filterTypes,
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
    if (typeSelectValues.length === 0) {
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
      topicSelectValues.map((t) => {
        uri += `&topic=${t}`;
        return true;
      });
    }
    if (yearSelectValues.length > 0) {
      yearSelectValues.map((t) => {
        uri += `&year=${t}`;
        return true;
      });
    }
    if (typeSelectValues.length > 0) {
      typeSelectValues.map((t) => {
        const filter = filterTypes.filter((f) => f.name === t);
        if (filter.length > 0) {
          filter[0].params.map((p) => {
            uri += `&${p.name}=${p.value}`;
            return true;
          });
        }
        return true;
      });
    }
    if (isSearchPage) {
      uri += '&searchpage=true';
    }

    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        const rows = data.items.filter(
          (v, i, a) => a.findIndex((t) => t.id === v.id) === i,
        );
        const aggregations = data.meta.aggregations;
        aggregations.topics = mergeObjects([
          aggregations.topics_contentpage,
          aggregations.topics_personpage,
        ]);

        this.setState(() => ({
          loading: false,
          loadingInitial: false,
          rows,
          aggregations: data.meta.aggregations,
          totalRows: data.meta.total_count,
        }));
      });
  }

  getAggregationCount(filterType) {
    const { aggregations } = this.state;
    let key = filterType.name;
    let type = 'contenttypes';
    if (Object.keys(filterType).includes('alias')) {
      key = filterType.alias;
    }
    if (Object.keys(filterType).includes('parent')) {
      type = 'contentsubtypes';
    }
    if (Object.keys(filterType).includes('aggregationField')) {
      type = filterType.aggregationField;
    }
    return aggregations[type][key];
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
    // Here we need to add fetch code for getting the years
    this.setState(() => ({
      loadingYears: false,
      years: Array.from({ length: 12 }, (_, i) => 2021 - i),
    }));
  }

  getTypes() {
    this.setState(() => ({
      loadingTypes: false,
    }));
  }

  getSubTypes(parentName) {
    return this.dropdownTypes.filter(
      (f) => f.parent && f.parent === parentName,
    );
  }

  setPage(page) {
    this.setState(
      () => ({
        currentPage: page,
      }),
      this.getRows,
    );
  }

  get dropdownTopics() {
    const { topics } = this.state;
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
    const { filterTypes } = this.props;
    const url = new URL(window.location);
    url.searchParams.set('query', searchValue);
    if (sortSelected) {
      url.searchParams.set('sort', sortSelected);
    } else {
      url.searchParams.delete('sort');
    }
    if (topicSelectValues.length > 0) {
      url.searchParams.delete('topic');
      topicSelectValues.map((t) => {
        url.searchParams.append('topic', t);
        return true;
      });
    } else {
      url.searchParams.delete('topic');
    }
    if (typeSelectValues.length > 0) {
      url.searchParams.delete('content_type');
      url.searchParams.delete('contenttype');
      url.searchParams.delete('contentsubtype');
      url.searchParams.delete('eventaccess');
      typeSelectValues.map((t) => {
        const filter = filterTypes.filter((f) => f.name === t);
        if (filter.length > 0) {
          filter[0].params.map((p) => {
            url.searchParams.append(p.name, p.value);
            return true;
          });
        }
        return true;
      });
    } else {
      url.searchParams.delete('content_type');
      url.searchParams.delete('contenttype');
      url.searchParams.delete('contentsubtype');
      url.searchParams.delete('eventaccess');
    }
    if (yearSelectValues.length > 0) {
      url.searchParams.delete('year');
      yearSelectValues.map((t) => {
        url.searchParams.append('year', t);
        return true;
      });
    } else {
      url.searchParams.delete('year');
    }
    window.history.pushState({}, '', url);
  }

  removeAllFilters() {
    this.setState(
      {
        topicSelectValues: [],
        typeSelectValues: [],
        yearSelectValues: [],
      },
      this.getRows,
    );
  }

  // eslint-disable-next-line class-methods-use-this
  toggleDropdown(e) {
    e.target.nextSibling.classList.toggle('show');
  }

  renderSelectedFilters() {
    const {
      topics, topicSelectValues, typeSelectValues, yearSelectValues,
    } = this.state;
    const filter = [];
    if (topicSelectValues.length > 0) {
      topicSelectValues.map((t) => {
        const topic = topics.filter((to) => to.id === t)[0];
        filter.push(
          <span
            className="filter"
            onClick={(e) => this.handleTopicSelect(e, t, false)}
            onKeyDown={(e) => this.handleTopicSelect(e, t, false)}
            role="button"
            tabIndex="0"
          >
            {topic.title}
            <i className="fa fa-times" />
          </span>,
        );
        return true;
      });
    }
    if (typeSelectValues.length > 0) {
      typeSelectValues.map((s) => {
        const parts = s.split('_');
        if (parts.length > 1) {
          filter.push(
            <span
              className="filter"
              onClick={(e) => this.handleTypeSelect(e, parts[0], parts[1], false)}
              onKeyDown={(e) => this.handleTypeSelect(e, parts[0], parts[1], false)}
              role="button"
              tabIndex="0"
            >
              {parts[1]}
              <i className="fa fa-times" />
            </span>,
          );
        } else {
          filter.push(
            <span
              className="filter"
              onClick={(e) => this.handleTypeSelect(e, s, undefined, false)}
              onKeyDown={(e) => this.handleTypeSelect(e, s, undefined, false)}
              role="button"
              tabIndex="0"
            >
              {s}
              <i className="fa fa-times" />
            </span>,
          );
        }
        return true;
      });
    }
    if (yearSelectValues.length > 0) {
      yearSelectValues.map((y) => {
        filter.push(
          <span
            className="filter"
            onClick={(e) => this.handleYearSelect(e, y, false)}
            onKeyDown={(e) => this.handleYearSelect(e, y, false)}
            role="button"
            tabIndex="0"
            key={y}
          >
            {y}
            <i className="fa fa-times" />
          </span>,
        );
        return true;
      });
    }
    if (filter.length > 0) {
      filter.push(
        <span
          className="filter red"
          onClick={this.removeAllFilters}
          onKeyDown={this.removeAllFilters}
          role="button"
          tabIndex="0"
        >
          Clear All
        </span>,
      );
    }

    return (
      <div className="filterlist">
        {filter.length > 0 ? (
          <div className="filtertitle">Selected Filters:</div>
        ) : (
          ''
        )}
        {filter}
      </div>
    );
  }

  renderSearchBar(showSidebar) {
    const { searchValue } = this.state;
    const { searchPlaceholder } = this.props;
    return (
      <div className="search-bar">
        <form className="search-bar-form" onSubmit={this.handleSearchSubmit}>
          <div className="form-row position-relative">
            <div className="col">
              <div
                className={`input-group input-group-search ${
                  showSidebar ? 'large' : ''
                }`}
              >
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
      </div>
    );
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
      aggregations,
      searchValue,
      sortSelected,
      topicsFilter,
      topicSelectValues,
      totalRows,
      typeSelectValues,
      years,
      yearSelectValues,
    } = this.state;
    const {
      blockListing,
      containerClass,
      hideTopicDropdown,
      filterTypes,
      RowComponent,
      showCount,
      showSearch,
      showSidebar,
      sortOptions,
      tableColumns,
    } = this.props;

    return (
      <div className="row search-table-container">
        {showSearch && (
          <div className="search-table search-table-mobile col-12 d-block d-md-none">
            {this.renderSearchBar(showSidebar)}
          </div>
        )}
        {showSidebar && (
          <div className="search-filters col-md-3">
            {!hideTopicDropdown && (
              <div className="dropdown custom-dropdown dropdown-topics keep-open">
                <button
                  className="dropdown-toggle"
                  type="button"
                  id="search-bar-topics"
                  onClick={(e) => this.toggleDropdown(e)}
                  aria-haspopup="true"
                  aria-expanded="false"
                >
                  Topics
                </button>
                <div
                  className="dropdown-menu pt-0"
                  aria-labelledby="search-bar-topics"
                >
                  <div className="topic-filter">
                    <div className="input-group input-group-search">
                      <input
                        type="text"
                        className="form-control"
                        placeholder="search topics"
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
                      {this.dropdownTopics
                        .filter(
                          (topic) => topicsFilter === ''
                            || topic.title
                              .toLowerCase()
                              .includes(topicsFilter.toLowerCase()),
                        )
                        .map((topic) => (
                          <li
                            className="dropdown-item"
                            key={`topic-${topic.id}`}
                          >
                            <label
                              htmlFor={`topic-${topic.id}`}
                              className={`keep-open ${
                                !aggregations.topics[topic.id] ? 'inactive' : ''
                              }`}
                            >
                              <input
                                id={`topic-${topic.id}`}
                                type="checkbox"
                                checked={
                                  topicSelectValues.includes(topic.id)
                                    ? 'checked'
                                    : ''
                                }
                                onChange={(e) => this.handleTopicSelect(e, topic.id)}
                              />
                              <span />
                              {topic.title}
                              &nbsp;
                              {aggregations.topics[topic.id] ? (
                                <>
                                  (
                                  {aggregations.topics[topic.id]}
                                  )
                                </>
                              ) : (
                                <>(0)</>
                              )}
                            </label>
                          </li>
                        ))}
                      {this.dropdownTopics.filter(
                        (topic) => topicsFilter === ''
                          || topic.title
                            .toLowerCase()
                            .includes(topicsFilter.toLowerCase()),
                      ).length === 0 && (
                        <li className="dropdown-item" key="noresults">
                          No results matching &quot;
                          {topicsFilter}
                          &quot;
                        </li>
                      )}
                    </ul>
                  )}
                </div>
              </div>
            )}
            {!loadingTypes && filterTypes.length > 0 && (
              <div className="dropdown custom-dropdown keep-open">
                <button
                  className="dropdown-toggle"
                  type="button"
                  id="search-bar-types"
                  onClick={(e) => this.toggleDropdown(e)}
                  aria-haspopup="true"
                  aria-expanded="false"
                >
                  Types
                </button>
                <div
                  className="dropdown-menu w-100"
                  aria-labelledby="search-bar-types"
                >
                  <ul>
                    {this.dropdownTypes.map(function(type) {
                      if (!Object.keys(type).includes('parent')) {
                        return (
                          <li
                            className="dropdown-item"
                            key={`type-${type.name.replace(' ', '_')}`}
                          >
                            <label
                              htmlFor={`input_type_${type.name}`}
                              className={`keep-open ${
                                !this.getAggregationCount(type)
                                  ? 'inactive'
                                  : ''
                              }`}
                            >
                              <input
                                id={`input_type_${type.name}`}
                                type="checkbox"
                                onChange={(e) => this.handleTypeSelect(e, type.name)}
                                className={`${
                                  typeSelectValues.some(
                                    (t) => t.split('_')[0] === type.name,
                                  )
                                    ? 'partial'
                                    : ''
                                }`}
                                checked={
                                  typeSelectValues.includes(type.name)
                                    ? 'checked'
                                    : ''
                                }
                              />
                              <span />
                              {type.name}
                              &nbsp;
                              {this.getAggregationCount(type) ? (
                                <>
                                  (
                                  {this.getAggregationCount(type)}
                                  )
                                </>
                              ) : (
                                <>(0)</>
                              )}
                            </label>
                            {this.getSubTypes(type.name)
                              && this.getSubTypes(type.name).length > 0 && (
                              <ul>
                                {this.getSubTypes(type.name).map(
                                  (subtype) => (
                                    <li
                                      className="dropdown-item"
                                      key={`subtype-${subtype.name.replace(
                                        ' ',
                                        '_',
                                      )}`}
                                    >
                                      <label
                                        htmlFor={`input_${type.name}_${subtype.name}`}
                                        className={`keep-open ${
                                          !this.getAggregationCount(subtype)
                                            ? 'inactive'
                                            : ''
                                        }`}
                                      >
                                        <input
                                          id={`input_${type.name}_${subtype.name}`}
                                          type="checkbox"
                                          onChange={(e) => this.handleTypeSelect(
                                            e,
                                            subtype.name,
                                          )}
                                          checked={
                                            typeSelectValues.includes(
                                              subtype.name,
                                            )
                                              ? 'checked'
                                              : ''
                                          }
                                          className={`${type.name} ${type.name}_${subtype.name}`}
                                        />
                                        <span />
                                        {subtype.name}
                                          &nbsp;
                                        {this.getAggregationCount(subtype) ? (
                                          <>
                                            (
                                            {this.getAggregationCount(
                                              subtype,
                                            )}
                                            )
                                          </>
                                        ) : (
                                          <>(0)</>
                                        )}
                                      </label>
                                    </li>
                                  ),
                                )}
                              </ul>
                            )}
                          </li>
                        );
                      }
                      return null;
                    }, this)}
                  </ul>
                </div>
              </div>
            )}

            <div className="dropdown custom-dropdown keep-open">
              <button
                className="dropdown-toggle"
                type="button"
                id="search-bar-years"
                onClick={(e) => this.toggleDropdown(e)}
                aria-haspopup="true"
                aria-expanded="false"
              >
                Years
              </button>
              <div className="dropdown-menu" aria-labelledby="search-bar-years">
                {!loadingYears && (
                  <ul className="columns-2">
                    {years.map((year) => (
                      <li className="dropdown-item" key={`year-${year}`}>
                        <label
                          htmlFor={`year-${year}`}
                          className={`keep-open ${
                            !aggregations.years[year] ? 'inactive' : ''
                          }`}
                        >
                          <input
                            type="checkbox"
                            id={`year-${year}`}
                            checked={
                              yearSelectValues.includes(year) ? 'checked' : ''
                            }
                            onChange={(e) => this.handleYearSelect(e, year)}
                          />
                          <span />
                          {year}
                          &nbsp;
                          {aggregations.years[year] ? (
                            <>
                              (
                              {aggregations.years[year]}
                              )
                            </>
                          ) : (
                            <>(0)</>
                          )}
                        </label>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}
        <div
          className={`search-table ${showSidebar ? 'col-md-9' : 'col-md-12'}`}
        >
          <div ref={this.searchTableRef} className="search-table-scroll" />
          {showSearch && (
            <div className="d-none d-md-block">
              {this.renderSearchBar(showSidebar)}
            </div>
          )}
          {loadingInitial ? (
            <SearchTableSkeleton />
          ) : rows.length ? (
            <>
              {showCount && totalRows && (
                <div className="search-table-count">
                  {`${totalRows} results for "${searchValue}"`}
                </div>
              )}
              {this.renderSelectedFilters()}

              <div className="search-bar-sort-wrapper">
                <span>Sort by:</span>
                <ul className="search-bar-sort-list">
                  {sortOptions.map((sortOption) => (
                    <li key={`sort-${sortOption.value}`}>
                      <button
                        type="button"
                        className={[
                          'search-bar-sort-link',
                          (sortSelected === sortOption.value
                            || (!sortSelected && sortOption.default))
                            && 'active',
                        ].join(' ')}
                        onClick={() => this.handleSortSelect(sortOption.value)}
                      >
                        {sortOption.name}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              {blockListing ? (
                <div
                  className={[
                    ...containerClass,
                    'search-results',
                    loading && 'loading',
                  ].join(' ')}
                >
                  {rows.map((row) => (
                    <RowComponent key={`${row.id}-${row.elevated}`} row={row} />
                  ))}
                </div>
              ) : (
                <table
                  className={[
                    ...containerClass,
                    'search-results',
                    loading && 'loading',
                  ].join(' ')}
                >
                  <thead>
                    <tr>
                      {tableColumns.map((tableColumn) => (
                        <th
                          colSpan={tableColumn.colSpan}
                          key={tableColumn.colTitle}
                        >
                          {tableColumn.colTitle}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <RowComponent
                        key={`${row.id}-${row.elevated}`}
                        row={row}
                      />
                    ))}
                  </tbody>
                </table>
              )}
            </>
          ) : (
            <>
              {this.renderSelectedFilters()}
              <p>
                Your query returned no results. Please check your spelling and
                try again.
              </p>
            </>
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
  endpointParams: PropTypes.arrayOf(
    PropTypes.shape({
      paramName: PropTypes.string,
      paramValue: PropTypes.any,
    }),
  ),
  fields: PropTypes.arrayOf(PropTypes.string).isRequired,
  filterTypes: PropTypes.arrayOf(
    PropTypes.shape({
      endpoint: PropTypes.string,
      name: PropTypes.string,
      params: PropTypes.arrayOf(
        PropTypes.shape({
          name: PropTypes.string,
          value: PropTypes.string,
        }),
      ),
    }),
  ),
  hideTopicDropdown: PropTypes.bool,
  isSearchPage: PropTypes.bool,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
  searchPlaceholder: PropTypes.string,
  showCount: PropTypes.bool,
  showSearch: PropTypes.bool,
  showSidebar: PropTypes.bool,
  sortOptions: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      value: PropTypes.string,
    }),
  ),
  tableColumns: PropTypes.arrayOf(
    PropTypes.shape({
      colSpan: PropTypes.number,
      colTitle: PropTypes.string,
    }),
  ),
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
  showSidebar: true,
  sortOptions: [
    {
      default: true,
      name: 'Date',
      value: 'date',
    },
  ],
  tableColumns: [],
};

export default SearchTable;
