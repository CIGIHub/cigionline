import PropTypes from 'prop-types';
import React from 'react';

import Paginator from './Paginator';

class SearchTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: 1,
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

    fetch(`/api${endpoint}/?limit=${limit}&offset=${offset}&fields=${fields}`)
      .then((res) => res.json())
      .then((data) => {
        this.setState(() => ({
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
    const { currentPage, rows } = this.state;
    const { containerClass, RowComponent } = this.props;

    return (
      <>
        <div className={containerClass}>
          {rows.map((row) => (
            <RowComponent key={row.id} row={row} />
          ))}
        </div>
        <Paginator currentPage={currentPage} totalPages={this.totalPages} setPage={this.setPage} />
      </>
    );
  }
}

SearchTable.propTypes = {
  containerClass: PropTypes.string.isRequired,
  endpoint: PropTypes.string.isRequired,
  fields: PropTypes.string.isRequired,
  limit: PropTypes.number,
  RowComponent: PropTypes.func.isRequired,
};

SearchTable.defaultProps = {
  limit: 24,
};

export default SearchTable;
