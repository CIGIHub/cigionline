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
      loadingTopics: true,
      rows: [],
      searchValue: '',
      years: [],
      yearSelectValue: null,
    };

    this.handleSearchValueChange = this.handleSearchValueChange.bind(this);
    this.handleYearSelect = this.handleYearSelect.bind(this);
  }

  componentDidMount() {
    this.getRows();
  }

  handleSearchValueChange(e) {
    this.setState({
      searchValue: e.target.value,
    });
  }

  handleYearSelect(id) {
    this.setState({
      yearSelectValue: id,
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

  // get dropdownSelectedYear() {
  //   const { years, yearSelectValue } = this.state;
  //   let selectedyear = 'All years';
  //   years.forEach((year) => {
  //     if (year.id === yearSelectValue) {
  //       selectedYear = year;
  //     }
  //   });
  //   return selectedTopic;
  // }

  // get dropdownTopics() {
  //   const { topics, topicSelectValue } = this.state;
  //   const dropdownTopics = [];
  //   topics.forEach((topic) => {
  //     if (topic.id !== topicSelectValue) {
  //       dropdownTopics.push(topic);
  //     }
  //   });
  //   if (topics.length !== dropdownTopics.length) {
  //     dropdownTopics.unshift({
  //       id: null,
  //       title: 'All Topics',
  //     });
  //   }
  //   return dropdownTopics;
  // }

  render() {
    const {
      loading,
      loadingInitial,
      loadingTopics,
      rows,
      searchValue,
      sortSelected,
    } = this.state;

    const sortOptions = [{
      default: true,
      name: 'Last Name',
      value: 'last_name',
    }, {
      name: 'First Name',
      value: 'first_name',
    }];

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
                  </button>
                  <div className="dropdown-menu" aria-labelledby="search-bar-topics">
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
              <table className={['custom-theme-table', 'table-experts', 'search-results', loading && 'loading'].join(' ')}>
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
                  {rows.map((row) => (
                    <AnnualReportListing key={row.year} row={row} />
                  ))}
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
