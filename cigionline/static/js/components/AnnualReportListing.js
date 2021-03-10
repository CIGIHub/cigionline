import PropTypes from 'prop-types';
import React from 'react';

function AnnualReportListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="4">
        <div className="table-mobile-text">
          Year
        </div>
        <div className="table-content">
          <a href={row.url}>
            {`${row.year} Annual Report`}
          </a>
        </div>
      </td>
      <td colSpan="2">
        {row.report_interactive && (
          <>
            <div className="table-mobile-text">
              Digital Interactive
            </div>
            <div className="table-content">
              <a className="button-action" href={row.report_interactive}>
                <i className="fas fa-mouse-pointer" />
                Explore
              </a>
            </div>
          </>
        )}
      </td>
      <td colSpan="2">
        {row.report_english && (
          <>
            <div className="table-mobile-text">
              English
            </div>
            <div className="table-content">
              <a className="table-btn-icon" href={row.report_english}>
                <i className="fas fa-download" />
              </a>
            </div>
          </>
        )}
      </td>
      <td colSpan="2">
        {row.report_french && (
          <>
            <div className="table-mobile-text">
              en français
            </div>
            <div className="table-content">
              <a className="table-btn-icon" href={row.report_french}>
                <i className="fas fa-download" />
              </a>
            </div>
          </>
        )}
      </td>
      <td colSpan="2">
        {row.report_financial && (
          <>
            <div className="table-mobile-text">
              Financial Statement
            </div>
            <div className="table-content">
              <a className="table-btn-icon" href={row.report_financial}>
                <i className="fas fa-download" />
              </a>
            </div>
          </>
        )}
      </td>
    </tr>
  );
}

AnnualReportListing.propTypes = {
  row: PropTypes.shape({
    year: PropTypes.number,
    report_english: PropTypes.string,
    report_french: PropTypes.string,
    report_interactive: PropTypes.string,
    report_financial: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
};

export default AnnualReportListing;
