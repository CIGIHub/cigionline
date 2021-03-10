import React from 'react';

import AnnualReportListing from './AnnualReportListing';
import SearchTableSkeleton from './SearchTableSkeleton';
import '../../css/components/SearchTable.scss';

class SearchTableAnnualReports extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      loadingInitial: true,
      rows: [],
      searchValue: '',
      years: [],
      yearSelected: 'All Years',
    };

    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleYearSelect = this.handleYearSelect.bind(this);
  }

  componentDidMount() {
    this.getRows();
  }

  handleSearchValueChange(e) {
    const { years } = this.state;
    const year = Number(e.target.value);
    if (years.includes(year)) {
      this.setState({
        searchValue: e.target.value,
        yearSelected: year,
      });
    } else {
      this.setState({
        searchValue: e.target.value,
        yearSelected: 'All Years',
      });
    }
  }

  handleYearSelect(year) {
    this.setState({
      yearSelected: year,
      searchValue: year,
    });
  }

  getRows() {
    this.setState(() => ({
      loading: true,
    }));

    fetch(encodeURI('/api/annual-reports/'))
      .then((res) => res.json())
      .then((data) => {
        const years = [];
        data.items.forEach((row) => {
          years.push(row.year);
        });
        this.setState(() => ({
          loading: false,
          loadingInitial: false,
          rows: data.items,
          years,
        }));
      });
  }

  render() {
    const {
      loading,
      loadingInitial,
      rows,
      searchValue,
      years,
      yearSelected,
    } = this.state;

    return (
      <div className="search-table">
        <div className="search-bar">
          <form className="search-bar-form">
            <div className="form-row position-relative">
              <div className="col">
                <div className="input-group input-group-search">
                  <input
                    type="text"
                    className="form-control"
                    value={searchValue}
                    placeholder="Search Annual Reports"
                    onChange={this.handleSearchValueChange}
                  />
                  <div className="input-group-append">
                    <button className="btn-search" type="submit">
                      <i className="far fa-search" />
                    </button>
                  </div>
                </div>
              </div>
              <div className="col-md-3 position-static">
                <div className="dropdown custom-dropdown dropdown-full-width">
                  <button className="dropdown-toggle" type="button" id="search-bar-topics" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    {yearSelected}
                  </button>
                  <div className="dropdown-menu" aria-labelledby="search-bar-topics">
                    <button
                      className="dropdown-item"
                      type="button"
                      onClick={() => this.handleYearSelect('All Years')}
                    >
                      All Years
                    </button>
                    {years.map((year) => (
                      <button
                        key={year}
                        className="dropdown-item"
                        type="button"
                        onClick={() => this.handleYearSelect(year)}
                      >
                        {year}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
        {loadingInitial
          ? <SearchTableSkeleton />
          : rows.length
            ? (
              <table className={['custom-theme-table', 'search-results', loading && 'loading'].join(' ')}>
                <thead>
                  <tr>
                    <th colSpan="4">Year</th>
                    <th colSpan="2">Digital Interactive</th>
                    <th colSpan="2">English</th>
                    <th colSpan="2">en français</th>
                    <th colSpan="2">Financial Statement</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => ((yearSelected === 'All Years' || row.year === yearSelected)
                    && <AnnualReportListing key={row.year} row={row} />))}
                </tbody>
              </table>
            ) : (
              <p>
                Your query returned no results. Please check your spelling and try again.
              </p>
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
export default SearchTableAnnualReports;
