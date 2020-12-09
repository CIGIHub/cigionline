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
    const { currentPage } = this.state;
    const { endpoint, fields, limit } = this.props;

    const offset = (currentPage - 1) * limit;

    this.setState(() => ({
      loading: true,
    }));
    this.searchResultsRef.current.scrollIntoView({ behavior: 'smooth' });

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
    const { containerClass, RowComponent } = this.props;

    return (
      <div className="search-table">
        {loadingInitial && <SearchTableSkeleton />}
        <div ref={this.searchResultsRef} className={[...containerClass, 'search-results', loading && 'loading'].join(' ')}>
          {rows.map((row) => (
            <RowComponent key={row.id} row={row} />
          ))}
        </div>
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
  containerClass: PropTypes.arrayOf(PropTypes.string).isRequired,
  endpoint: PropTypes.string.isRequired,
  fields: PropTypes.string.isRequired,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
};

SearchTable.defaultProps = {
  limit: 24,
};

export default SearchTable;
