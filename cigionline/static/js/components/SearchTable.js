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
      rows: [],
      totalRows: 0,
    };
  }

  componentDidMount() {
    this.getRows();
  }

  getRows() {
    const { currentPage, loadingInitial } = this.state;
    const { endpoint, fields, limit } = this.props;

    const offset = (currentPage - 1) * limit;

    this.setState(() => ({
      loading: true,
    }));
    if (!loadingInitial) {
      this.searchResultsRef.current.scrollIntoView({ behavior: 'smooth' });
    }

    fetch(`/api${endpoint}/?limit=${limit}&offset=${offset}&fields=${fields}`)
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

  setPage(page) {
    this.setState(() => ({
      currentPage: page,
    }), this.getRows);
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
      rows,
    } = this.state;
    const {
      blockListing,
      containerClass,
      RowComponent,
      tableColumns,
    } = this.props;

    return (
      <div className="search-table">
        {loadingInitial && <SearchTableSkeleton />}
        {blockListing
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
  fields: PropTypes.string.isRequired,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
  tableColumns: PropTypes.arrayOf(PropTypes.shape({
    colSpan: PropTypes.number,
    colTitle: PropTypes.string,
  })),
};

SearchTable.defaultProps = {
  blockListing: false,
  limit: 24,
  tableColumns: [],
};

export default SearchTable;
