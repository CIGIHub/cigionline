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
class SearchTableBlockListing extends React.Component {
  constructor(props) {
    super(props);
    this.searchTableRef = React.createRef();
    this.state = {
      currentPage: 1,
      expertSelectValues: [],
      loading: true,
      loadingInitial: true,
      rows: [],
      searchValue: '',
      topicSelectValues: [],
      typeSelectValues: [],
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
  }

  componentDidMount() {
    this.getRows();
  }

  getRows() {
    const {
      currentPage,
      loadingInitial,
      searchValue,
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

  setPage(page) {
    this.setState(
      () => ({
        currentPage: page,
      }),
      this.getRows,
    );
  }

  get totalPages() {
    const { limit } = this.props;
    const { totalRows } = this.state;
    return Math.ceil(totalRows / limit);
  }

  renderBlockListing(RowComponent, containerClass) {
    const { rows, loading } = this.state;
    return (
      <div
        className={[
          ...containerClass,
          loading && 'loading',
        ].join(' ')}
      >
        {rows.map((row) => (
          <div className="col">
            <RowComponent key={`${row.id}-${row.elevated}`} row={row} />
          </div>
        ))}
      </div>
    );
  }

  render() {
    const {
      currentPage,
      loading,
      loadingInitial,
      rows,
    } = this.state;
    const {
      blockListing,
      containerClass,
      RowComponent,
    } = this.props;

    return (
      <div className="search-table-container custom-theme-table">
        <div className="search-table">
          <div ref={this.searchTableRef} className="search-table-scroll" />
          {loadingInitial ? (
            <SearchTableSkeleton />
          ) : rows.length && (
            <>
              {blockListing && this.renderBlockListing(RowComponent, containerClass)}
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

SearchTableBlockListing.propTypes = {
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
  isSearchPage: PropTypes.bool,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
};

SearchTableBlockListing.defaultProps = {
  blockListing: false,
  containerClass: [],
  contentsubtypes: [],
  contenttypes: [],
  endpointParams: [],
  filterTypes: [],
  isSearchPage: false,
  limit: 24,
};

export default SearchTableBlockListing;
