import PropTypes from 'prop-types';
import React from 'react';

import '../../css/components/Paginator.scss';

class Paginator extends React.Component {
  get hasNextPage() {
    const { currentPage, totalPages } = this.props;
    return currentPage < totalPages;
  }

  get hasPrevPage() {
    const { currentPage } = this.props;
    return currentPage > 1;
  }

  get pageNumbers() {
    const { currentPage, totalPages } = this.props;

    const pageNumbers = [currentPage];
    if (currentPage > 1) {
      for (const i of Array(Math.max(2, currentPage - (totalPages - 4))).keys()) {
        if (currentPage - (i + 1) >= 1) {
          pageNumbers.push(currentPage - (i + 1));
        }
      }
    }
    if (currentPage < totalPages) {
      for (const i of Array(5 - pageNumbers.length).keys()) {
        if (currentPage + (i + 1) <= totalPages) {
          pageNumbers.push(currentPage + (i + 1));
        }
      }
    }
    pageNumbers.sort((a, b) => a - b);
    return pageNumbers.map((page) => ({
      current: page === currentPage,
      page,
    }));
  }

  render() {
    const { currentPage, setPage, totalPages } = this.props;

    return (
      <div className="pagination-links-numbered">
        {this.hasPrevPage && (
          <>
            <li key="first" className="pagination-link-first pagination-underline">
              <button type="button" onClick={() => setPage(1)}>
                First
              </button>
            </li>
            <li key="previous" className="pagination-underline pagination-underline-centred">
              <button type="button" onClick={() => setPage(currentPage - 1)}>
                <i className="fa fa-arrow-left" />
              </button>
            </li>
          </>
        )}
        {this.pageNumbers.map((pageNumber) => (
          pageNumber.current
            ? (
              <li key={`page-${pageNumber.page}`} className="active pagination-underline pagination-underline-centred">
                <span>
                  {pageNumber.page}
                </span>
              </li>
            ) : (
              <li key={`page-${pageNumber.page}`}>
                <button type="button" onClick={() => setPage(pageNumber.page)}>
                  {pageNumber.page}
                </button>
              </li>
            )
        ))}
        {this.hasNextPage && (
          <>
            <li key="next" className="pagination-underline pagination-underline-centred">
              <button type="button" onClick={() => setPage(currentPage + 1)}>
                <i className="fa fa-arrow-right" />
              </button>
            </li>
            <li key="last" className="pagination-link-last pagination-underline">
              <button type="button" onClick={() => setPage(totalPages)}>
                Last
              </button>
            </li>
          </>
        )}
      </div>
    );
  }
}

Paginator.propTypes = {
  currentPage: PropTypes.number.isRequired,
  setPage: PropTypes.func.isRequired,
  totalPages: PropTypes.number.isRequired,
};

export default Paginator;
