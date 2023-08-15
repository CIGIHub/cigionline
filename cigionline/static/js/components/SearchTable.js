import PropTypes from 'prop-types';
import React from 'react';

import Paginator from './Paginator';
import SearchTableSkeleton from './SearchTableSkeleton';
import SearchResultListingRow from './SearchResultListingRow';
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
    const { filterTypes, isSearchPage } = props;
    this.state = {
      currentPage: 1,
      currentYear: 0,
      emptyQuery: false,
      expertsFilter: '',
      expertSelectValues: [],
      filterTypes,
      isSearchPage,
      loading: true,
      loadingInitial: true,
      loadingExperts: true,
      loadingTopics: true,
      loadingYears: true,
      loadingTypes: true,
      rows: [],
      searchValue: '',
      showFilters: false,
      sortSelected: 'Date',
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
        experts: {},
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
    const { isSearchPage, showSidebar } = this.props;
    if (isSearchPage) {
      const params = new URL(window.location).searchParams;
      const query = params.get('query');
      const sort = params.get('sort');
      const expert = params.getAll('expert').map((t) => parseInt(t, 10));
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
      if (expert.length > 0) {
        initialState.expertSelectValues = expert;
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
        initialState.typeSelectValues =
          initialState.typeSelectValues.concat(subtype);
      }
      if (year.length > 0) {
        initialState.yearSelectValues = year;
      }
      if (query) {
        this.setState(initialState, this.getRows);
      } else {
        this.setState({
          loadingInitial: false,
          loading: false,
          emptyQuery: true,
        });
      }
    } else {
      this.getRows();
    }
    if (showSidebar) {
      this.getExperts();
      this.getTopics();
      this.getTypes();
    }
  }

  handleSearchSubmit(e) {
    const { searchValue } = this.state;
    e.preventDefault();
    if (searchValue) {
      // When searching, set the page to the first page to display the most
      // relevant results. Note that setPage will also call the API to update the
      // table.
      this.setPage(1);
    }
  }

  handleSearchValueChange(e) {
    this.setState(
      {
        searchValue: e.target.value,
      },
      this.setPage(1),
    );
  }

  handleSortSelect(sortValue) {
    this.setState(
      {
        sortSelected: sortValue,
      },
      this.getRows,
    );
  }

  handleExpertSelect(e, id, checkOverride) {
    const { expertSelectValues } = this.state;
    let experts = expertSelectValues;
    if (e.target.checked || checkOverride) {
      experts.push(id);
    } else {
      experts = experts.filter((f) => f !== id);
    }
    this.setState(
      {
        expertSelectValues: experts,
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
        if (this.getAggregationCount(s) > 0) {
          types.push(s.name);
        }
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

  handleExpertsFilter(e) {
    this.setState(() => ({
      expertsFilter: e.target.value,
    }));
  }

  getRows() {
    const {
      currentPage,
      loadingInitial,
      searchValue,
      sortSelected,
      expertSelectValues,
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
    if (expertSelectValues.length > 0) {
      expertSelectValues.map((t) => {
        uri += `&expert=${t}`;
        return true;
      });
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
          loadingYears: false,
          years: Array.from({ length: 12 }, (_, i) => data.meta.current_year - i),
        }));
      });

    // using fixtures to test
    // const rows = fixtures.items.filter(
    //   (v, i, a) => a.findIndex((t) => t.id === v.id) === i,
    // );
    // const aggregations = fixtures.meta.aggregations;
    // aggregations.topics = mergeObjects([
    //   aggregations.topics_contentpage,
    //   aggregations.topics_personpage,
    // ]);
    // this.setState(() => ({
    //   loading: false,
    //   loadingInitial: false,
    //   rows,
    //   aggregations: fixtures.meta.aggregations,
    //   totalRows: fixtures.meta.total_count,
    // }));
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

  getExperts() {
    fetch(encodeURI('/api/all_experts_search/'))
      .then((res) => res.json())
      .then((data) => {
        this.setState(() => ({
          loadingExperts: false,
          experts: data.items.map((expert) => ({
            id: expert.id,
            title: expert.title,
          })),
        }));
      });
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

  get dropdownExperts() {
    const { experts } = this.state;
    const dropdownExperts = [];
    experts.forEach((expert) => {
      dropdownExperts.push(expert);
    });
    if (experts.length !== dropdownExperts.length) {
      dropdownExperts.unshift({
        id: null,
        title: 'All Experts',
      });
    }
    return dropdownExperts;
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
      expertSelectValues,
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
    if (expertSelectValues.length > 0) {
      url.searchParams.delete('expert');
      expertSelectValues.map((t) => {
        url.searchParams.append('expert', t);
        return true;
      });
    } else {
      url.searchParams.delete('expert');
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
        expertSelectValues: [],
        topicSelectValues: [],
        typeSelectValues: [],
        yearSelectValues: [],
      },
      this.getRows,
    );
  }

  toggleFiltersDropdown() {
    const { showFilters } = this.state;
    this.setState(() => ({
      showFilters: !showFilters,
    }));
  }

  // eslint-disable-next-line class-methods-use-this
  toggleDropdown(e) {
    const targetButton = e.target;
    const targetMenu = targetButton.nextSibling;
    const siblings = Array.from(
      targetButton.parentNode.parentNode.querySelectorAll('.dropdown'),
    ).filter((s) => s !== targetMenu.parentNode);
    for (let i = 0; i < siblings.length; i += 1) {
      siblings[i].querySelector('.dropdown-menu').classList.remove('show');
    }
    targetMenu.classList.toggle('show');
    if (targetButton.getAttribute('aria-expanded') === 'true') {
      targetButton.setAttribute('aria-expanded', false);
    } else {
      targetButton.setAttribute('aria-expanded', true);
    }
  }

  renderSelectedFilters() {
    const {
      experts,
      topics,
      expertSelectValues,
      topicSelectValues,
      typeSelectValues,
      yearSelectValues,
    } = this.state;
    const filter = [];
    if (expertSelectValues.length > 0) {
      expertSelectValues.map((t) => {
        const expert = experts.filter((to) => to.id === t)[0];
        filter.push(
          <button
            className="filter button--rounded"
            onClick={(e) => this.handleExpertSelect(e, t, false)}
            onKeyDown={(e) => this.handleExpertSelect(e, t, false)}
            type="button"
            tabIndex="0"
            key={`expert-filter-${expert.id}`}
          >
            {expert.title}
            <i className="fal fa-times" />
          </button>,
        );
        return true;
      });
    }
    if (topicSelectValues.length > 0) {
      topicSelectValues.map((t) => {
        const topic = topics.filter((to) => to.id === t)[0];
        filter.push(
          <button
            className="filter button--rounded"
            onClick={(e) => this.handleTopicSelect(e, t, false)}
            onKeyDown={(e) => this.handleTopicSelect(e, t, false)}
            type="button"
            tabIndex="0"
            key={`topic-filter-${topic.id}`}
          >
            {topic.title}
            <i className="fal fa-times" />
          </button>,
        );
        return true;
      });
    }
    if (typeSelectValues.length > 0) {
      typeSelectValues.map((s) => {
        const parts = s.split('_');
        if (parts.length > 1) {
          filter.push(
            <button
              className="filter button--rounded"
              onClick={(e) =>
                this.handleTypeSelect(e, parts[0], parts[1], false)
              }
              onKeyDown={(e) =>
                this.handleTypeSelect(e, parts[0], parts[1], false)
              }
              type="button"
              tabIndex="0"
              key={parts[1]}
            >
              {parts[1]}
              <i className="fal fa-times" />
            </button>,
          );
        } else {
          filter.push(
            <button
              className="filter button--rounded"
              onClick={(e) => this.handleTypeSelect(e, s, undefined, false)}
              onKeyDown={(e) => this.handleTypeSelect(e, s, undefined, false)}
              type="button"
              tabIndex="0"
              key={s}
            >
              {s}
              <i className="fal fa-times" />
            </button>,
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
            <i className="fal fa-times" />
          </span>,
        );
        return true;
      });
    }
    if (filter.length > 0) {
      filter.push(
        <button
          className="filter button--rounded button--clear"
          onClick={this.removeAllFilters}
          onKeyDown={this.removeAllFilters}
          type="button"
          tabIndex="0"
          key="clear-all"
        >
          Clear All
        </button>,
      );
    }

    return (
      filter.length > 0 && (
        <div className="filterlist">
          <div className="filtertitle">Selected Filters:</div>
          {filter}
        </div>
      )
    );
  }

  renderSearchBar(showSidebar) {
    const {
      expertsFilter,
      loadingExperts,
      loadingTopics,
      loadingYears,
      loadingTypes,
      aggregations,
      rows,
      searchValue,
      showFilters,
      topicsFilter,
      expertSelectValues,
      topicSelectValues,
      typeSelectValues,
      years,
      yearSelectValues,
    } = this.state;
    const {
      searchPlaceholder,
      showExpertDropDown,
      hideTopicDropdown,
      filterTypes,
      isSearchPage,
    } = this.props;
    return (
      <>
        {isSearchPage ? (
          <>
            <div
              className={`search-bar search-page__search-bar row gy-2 gx-5 g-lg-4 g-xl-5 ${
                showFilters ? 'show-filters' : ''
              }`}
            >
              <div className="col-12 search-bar__input-container">
                <form
                  className="search-bar-form"
                  onSubmit={this.handleSearchSubmit}
                >
                  <button className="btn-search" type="submit">
                    <i className="far fa-search" />
                  </button>
                  <input
                    type="text"
                    className="form-control"
                    value={searchValue}
                    placeholder={searchPlaceholder}
                    onChange={this.handleSearchValueChange}
                    required="required"
                  />
                </form>
              </div>
            </div>
            {rows.length > 0 && (
              <>
                <div className="search-bar__filter-by-label">Filter by:</div>
                {this.renderFilters()}
              </>
            )}
          </>
        ) : (
          <>
            <div
              className={`search-bar row gy-2 gx-5 g-lg-4 g-xl-5 ${
                showFilters ? 'show-filters' : ''
              }`}
            >
              <div className="col-lg-8 search-bar__input-container">
                <form
                  className="search-bar-form"
                  onSubmit={this.handleSearchSubmit}
                >
                  <button className="btn-search" type="submit">
                    <i className="far fa-search" />
                  </button>
                  <input
                    type="text"
                    className="form-control"
                    value={searchValue}
                    placeholder={searchPlaceholder}
                    onChange={this.handleSearchValueChange}
                    required="required"
                  />
                </form>
              </div>
              <div
                className="search-bar__filters-button search-filters col-lg-3 d-flex"
                id="search-bar__filters"
              >
                <button
                  type="button"
                  className="search-bar__filters__dropdown"
                  onClick={() => this.toggleFiltersDropdown()}
                >
                  <div>
                    <i className="fal fa-sort-amount-down" />
                    <span>Filters</span>
                  </div>
                  <i className="fal fa-angle-down" />
                </button>
              </div>
            </div>
            {showFilters && this.renderFilters()}
          </>
        )}
      </>
    );
  }

  renderResults(RowComponent, RowComponentList, containerClass) {
    const { rows, loading } = this.state;
    const { tableColumns } = this.props;
    return (
      <div
        className={[
          ...containerClass,
          'search-table__results',
          loading && 'loading',
        ].join(' ')}
      >
        <table>
          <thead>
            <tr>
              {tableColumns.length > 0 ? (
                tableColumns.map((column) => (
                  <th
                    key={column.colTitle}
                    className={`search-table__results__row__${column.colClass}`}
                  >
                    {column.colTitle}
                  </th>
                ))
              ) : (
                <>
                  <th className="search-table__results__row__title">Title</th>
                  <th className="search-table__results__row__content-type">
                    Content Type
                  </th>
                  <th className="search-table__results__row__authors">
                    Author
                  </th>
                  <th className="search-table__results__row__topics">
                    Topic
                  </th>
                  <th className="search-table__results__row__download"> </th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <RowComponentList
                key={`${row.id}-${row.elevated}`}
                row={row}
              />
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  renderBlockListing(RowComponent, containerClass) {
    const { rows, loading } = this.state;
    return (
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
    );
  }

  renderFilters() {
    const {
      aggregations,
      expertsFilter,
      loadingExperts,
      loadingTopics,
      loadingYears,
      loadingTypes,
      topicsFilter,
      expertSelectValues,
      topicSelectValues,
      typeSelectValues,
      years,
      yearSelectValues,
    } = this.state;
    const {
      searchPlaceholder,
      showExpertDropDown,
      hideTopicDropdown,
      filterTypes,
      isSearchPage,
    } = this.props;
    return (
      <div className="search-table__filters">
        <div className="search-table__filters__row">
          {showExpertDropDown && (
            <div className="dropdown custom-dropdown">
              <button
                className="search-table__filters__dropdown-toggle"
                type="button"
                id="search-bar-experts"
                onClick={(e) => this.toggleDropdown(e)}
                aria-haspopup="true"
                aria-expanded="false"
              >
                Experts
              </button>
              <div
                className="dropdown-menu"
                aria-labelledby="search-bar-experts"
              >
                {!loadingExperts && (
                  <ul>
                    {this.dropdownExperts
                      .filter(
                        (expert) =>
                          aggregations.experts[expert.id] > 0 &&
                          (expertsFilter === '' ||
                            expert.title
                              .toLowerCase()
                              .includes(expertsFilter.toLowerCase())),
                      )
                      .sort(
                        (a, b) =>
                          aggregations.experts[b.id] -
                          aggregations.experts[a.id],
                      )
                      .map((expert) => (
                        <li
                          className="dropdown-item"
                          key={`expert-${expert.id}`}
                        >
                          <label
                            htmlFor={`expert-${expert.id}`}
                            className={`keep-open ${
                              !aggregations.experts[expert.id] ? 'inactive' : ''
                            }`}
                          >
                            <input
                              id={`expert-${expert.id}`}
                              type="checkbox"
                              checked={
                                expertSelectValues.includes(expert.id)
                                  ? 'checked'
                                  : ''
                              }
                              onChange={(e) =>
                                this.handleExpertSelect(e, expert.id)
                              }
                            />
                            <span>{expert.title}</span>
                            <span className="dropdown-item__count">
                              {aggregations.experts[expert.id] ? (
                                <>{aggregations.experts[expert.id]}</>
                              ) : (
                                <>0</>
                              )}
                            </span>
                          </label>
                        </li>
                      ))}
                    {this.dropdownExperts.filter(
                      (expert) =>
                        expertsFilter === '' ||
                        expert.title
                          .toLowerCase()
                          .includes(expertsFilter.toLowerCase()),
                    ).length === 0 && (
                      <li className="dropdown-item" key="noresults">
                        No results matching &quot;
                        {expertsFilter}
                        &quot;
                      </li>
                    )}
                  </ul>
                )}
              </div>
            </div>
          )}
          {!hideTopicDropdown && (
            <div className="dropdown custom-dropdown dropdown-topics">
              <button
                className="search-table__filters__dropdown-toggle"
                type="button"
                id="search-bar-topics"
                onClick={(e) => this.toggleDropdown(e)}
                aria-haspopup="true"
                aria-expanded="false"
              >
                Topics
              </button>
              <div
                className="dropdown-menu"
                aria-labelledby="search-bar-topics"
              >
                {!loadingTopics && (
                  <ul>
                    {this.dropdownTopics
                      .filter(
                        (topic) =>
                          topicsFilter === '' ||
                          topic.title
                            .toLowerCase()
                            .includes(topicsFilter.toLowerCase()),
                      )
                      .map((topic) => (
                        <li className="dropdown-item" key={`topic-${topic.id}`}>
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
                              onChange={(e) =>
                                this.handleTopicSelect(e, topic.id)
                              }
                            />
                            <span>{topic.title}</span>
                            <span className="dropdown-item__count">
                              {aggregations.topics[topic.id] ? (
                                <>{aggregations.topics[topic.id]}</>
                              ) : (
                                <>0</>
                              )}
                            </span>
                          </label>
                        </li>
                      ))}
                    {this.dropdownTopics.filter(
                      (topic) =>
                        topicsFilter === '' ||
                        topic.title
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
            <div className="dropdown custom-dropdown">
              <button
                className="search-table__filters__dropdown-toggle"
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
                  {this.dropdownTypes.map(function (type) {
                    if (!Object.keys(type).includes('parent')) {
                      return (
                        <li
                          className="dropdown-item"
                          key={`type-${type.name.replace(' ', '_')}`}
                        >
                          <label
                            htmlFor={`input_type_${type.name}`}
                            className={`keep-open ${
                              !this.getAggregationCount(type) ? 'inactive' : ''
                            }`}
                          >
                            <input
                              id={`input_type_${type.name}`}
                              type="checkbox"
                              onChange={(e) =>
                                this.handleTypeSelect(e, type.name)
                              }
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
                            <span>{type.name}</span>
                            <span className="dropdown-item__count">
                              {this.getAggregationCount(type) ? (
                                <>{this.getAggregationCount(type)}</>
                              ) : (
                                <>0</>
                              )}
                            </span>
                          </label>
                          {this.getSubTypes(type.name) &&
                            this.getSubTypes(type.name).length > 0 && (
                              <ul>
                                {this.getSubTypes(type.name).map((subtype) => (
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
                                        onChange={(e) =>
                                          this.handleTypeSelect(e, subtype.name)
                                        }
                                        checked={
                                          typeSelectValues.includes(
                                            subtype.name,
                                          )
                                            ? 'checked'
                                            : ''
                                        }
                                        className={`${type.name} ${type.name}_${subtype.name}`}
                                      />
                                      <span>{subtype.name}</span>
                                      <span className="dropdown-item__count">
                                        {this.getAggregationCount(subtype) ? (
                                          <>
                                            {this.getAggregationCount(subtype)}
                                          </>
                                        ) : (
                                          <>0</>
                                        )}
                                      </span>
                                    </label>
                                  </li>
                                ))}
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
          <div className="dropdown dropdown-year custom-dropdown">
            <button
              className="search-table__filters__dropdown-toggle"
              type="button"
              id="search-bar-years"
              onClick={(e) => this.toggleDropdown(e)}
              aria-haspopup="true"
              aria-expanded="false"
            >
              Years
            </button>
            <div
              className="dropdown-menu dropdown-menu-years"
              aria-labelledby="search-bar-years"
            >
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
                        <span>{year}</span>
                        <span className="dropdown-item__count">
                          {aggregations.years[year] ? (
                            <>{aggregations.years[year]}</>
                          ) : (
                            <>0</>
                          )}
                        </span>
                      </label>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  render() {
    const {
      currentPage,
      emptyQuery,
      expertsFilter,
      loading,
      loadingExperts,
      loadingInitial,
      loadingTopics,
      loadingYears,
      loadingTypes,
      rows,
      aggregations,
      searchValue,
      sortSelected,
      topicsFilter,
      expertSelectValues,
      topicSelectValues,
      totalRows,
      typeSelectValues,
      years,
      yearSelectValues,
    } = this.state;
    const {
      blockListing,
      containerClass,
      filterTypes,
      showExpertDropDown,
      hideTopicDropdown,
      isSearchPage,
      RowComponent,
      RowComponentList,
      showCount,
      showSearch,
      showSidebar,
      sortOptions,
    } = this.props;

    return (
      <div className="search-table-container custom-theme-table">
        <div className="search-table">
          <div ref={this.searchTableRef} className="search-table-scroll" />
          {showSearch && <>{this.renderSearchBar(showSidebar)}</>}
          {loadingInitial ? (
            <SearchTableSkeleton />
          ) : rows.length ? (
            <>
              {showCount && totalRows && (
                <div className="search-table-count">
                  {`${totalRows} results for ${searchValue}. For exact matches, enclose search terms in double quotation marks (e.g. "platform governance").`}
                </div>
              )}
              <div className="search-table__filters__container">
                {this.renderSelectedFilters()}

                <div className="search-bar-sort-wrapper">
                  {sortOptions.length > 1 && (
                    <>
                      <div className="search-bar__sort__label">Sort by:</div>
                      <div className="search-bar-sort-list dropdown custom-dropdown">
                        <button
                          type="button"
                          className="dropdown-toggle"
                          data-bs-toggle="dropdown"
                          aria-expanded="false"
                        >
                          {sortSelected}
                        </button>
                        <ul className="dropdown-menu">
                          {sortOptions.map((sortOption) => (
                            <li
                              key={`sort-${sortOption.value}`}
                              className="dropdown-item"
                            >
                              <button
                                type="button"
                                className={[
                                  'search-bar-sort-link',
                                  (sortSelected === sortOption.value ||
                                    (!sortSelected && sortOption.default)) &&
                                    'active',
                                ].join(' ')}
                                onClick={() =>
                                  this.handleSortSelect(sortOption.value)
                                }
                              >
                                {sortOption.name}
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}
                </div>
              </div>
              {blockListing
                ? this.renderBlockListing(RowComponent, containerClass)
                : this.renderResults(RowComponent, RowComponentList, containerClass)}
            </>
          ) : emptyQuery ? (
            <div className="row">
              <div className="col-12">
                <p className="empty-query-prompt">
                  Please enter your search terms into the Search field. For
                  exact matches, enclose search terms in double quotation marks
                  (e.g. &quot;platform governance&quot;).
                </p>
              </div>
            </div>
          ) : (
            <>
              {this.renderSelectedFilters()}
              <p className="empty-query-prompt">
                Your query returned no results. Please check your spelling and
                try again.
              </p>
            </>
          )}
          {this.totalPages > 1 && (
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
  showExpertDropDown: PropTypes.bool,
  hideTopicDropdown: PropTypes.bool,
  isSearchPage: PropTypes.bool,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
  RowComponentList: PropTypes.func,
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
      colClass: PropTypes.string,
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
  showExpertDropDown: false,
  hideTopicDropdown: false,
  isSearchPage: false,
  limit: 24,
  RowComponentList: SearchResultListingRow,
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
