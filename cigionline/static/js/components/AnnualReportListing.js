import PropTypes from 'prop-types';
import React from 'react';

function AnnualReportListing(props) {
  const { row } = props;

  return (
    <tr>
      <td colSpan="4">
        <a href={row.url}>
          {`${row.year} Annual Report`}
        </a>
      </td>
      <td colSpan="2">
        {row.report_interactive && (
          <a className="button-action" href={row.report_interactive}>
            <i className="fas fa-mouse-pointer" />
            Explore
          </a>
        )}
      </td>
      <td colSpan="2">
        {row.report_english && (
          <a className="table-btn-icon" href={row.report_english}>
            <i className="fas fa-download" />
          </a>
        )}
      </td>
      <td colSpan="2">
        {row.report_french && (
          <a className="table-btn-icon" href={row.report_french}>
            <i className="fas fa-download" />
          </a>
        )}
      </td>
      <td colSpan="2">
        {row.report_financial && (
          <a className="table-btn-icon" href={row.report_financial}>
            <i className="fas fa-download" />
          </a>
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
