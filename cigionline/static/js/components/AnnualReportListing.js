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
              <a className="button-action track-cta" data-cta="ar-interactive" href={`https://www.cigionline.org${row.report_interactive}`}>
                <i className="fas fa-mouse-pointer" />
                Explore
              </a>
            </div>
          </>
        )}
      </td>
      <td colSpan="2">
        <div className="table-mobile-text">
          English
        </div>
        <div className="table-content">
          {(row.report_english && (
            <a className="button-action table-btn-icon track-cta" data-cta="ar-eng" href={row.report_english}>
              <i className="fas fa-download" />
            </a>
          )) || (
            <a className="table-btn-icon" href={`https://www.cigionline.org${row.report_interactive}en`}>
              <i className="fas fa-mouse-pointer" />
            </a>
          )}
        </div>
      </td>
      <td colSpan="2">
        <div className="table-mobile-text">
          en français
        </div>
        <div className="table-content">
          {(row.report_french && (
            <a className="button-action table-btn-icon track-cta" data-cta="ar-fr" href={row.report_french}>
              <i className="fas fa-download" />
            </a>
          )) || (
            <a className="button-action table-btn-icon track-cta" data-cta="ar-interactive" href={`https://www.cigionline.org${row.report_interactive}fr`}>
              <i className="fas fa-mouse-pointer" />
            </a>
          )}
        </div>
      </td>
      <td colSpan="2">
        {row.report_financial && (
          <>
            <div className="table-mobile-text">
              Financial Statement
            </div>
            <div className="table-content">
              <a className="button-action table-btn-icon track-cta" data-cta="ar-financial" href={row.report_financial}>
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
