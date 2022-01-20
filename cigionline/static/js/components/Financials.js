/* eslint-disable no-unused-vars, consistent-return, array-callback-return */
import React, { Fragment, useState } from 'react';
import queryString from 'query-string';
import {
  getLanguage,
  getSiteUrl,
} from './AnnualReportUtils';

const Financials = ({
  slide, slides, isOpen, contentOpacity, navigateToSlide,
}) => {
  const originUrl = window.location.origin;
  const currentPath = window.location.pathname;
  const params = queryString.parse(window.location.search);
  const type = params.tabtype ? params.tabtype : 'auditors-report';
  const [tabtype, settabtype] = useState(type);

  const language = getLanguage();
  const siteUrl = getSiteUrl();

  function loadTabs() {
    return slide.value.tabs.map((tab) => {
      const title = tab.value.title.split(' ').join('-').replace(/'/g, '').toLocaleLowerCase();
      const hrefUrl = `?tabtype=${title}/`;
      return (
        tabtype === title
          ? (
            <>
              {tab.value.title}
              <span className="menu-break">/</span>
            </>
          )
          : (
            <>
              <a
                href={hrefUrl}
                onClick={(e) => { e.preventDefault(); settabtype(title); window.history.pushState({}, '', `${originUrl}${currentPath}?tabtype=${title}`); }}
              >
                <span className="underline">
                  {tab.value.title}
                </span>
              </a>
              <span className="menu-break">/</span>
            </>
          )
      );
    });
  }

  function isNumber(n) {
    return /^-?[\d.]+(?:e-?\d+)?$/.test(n);
  }

  function getClassName(content, index) {
    if (index === 0) {
      return 'text-col';
    }
    const data = content.replace(/[^\d\.\-]/g, ''); // eslint-disable-line
    if (data) {
      if (!isNaN(data)) {
        return 'num-col';
      }
      return 'text-col';
    }
    return 'num-col dollar-sign';
  }

  function getRowClassName(trow) {
    if (trow[0] === '' && trow[2] && trow[4]) {
      return 'table-subtotal';
    }
    if (trow[0].indexOf('Total') > -1 && trow[2] && trow[4]) {
      return 'table-total';
    }

    if (trow[4] === '') {
      return 'table-subtitle';
    }
    return 'table-line-entry';
  }

  function firstHalfBody() {
    return slide.value.tabs.map(function(tab) {
      let title = tab.value.title.split(' ').join('-');
      title = title.replace(/'/g, '');
      title = title.toLocaleLowerCase();
      if (tabtype === title) {
        const half = Math.ceil(tab.value.body.length / 2);
        const firstHalf = tab.value.body.slice(0, half);
        return firstHalf
          .map(function(paragraph) {
            return paragraph.value;
          })
          .join('');
      }
    });
  }

  function secondHalfBody() {
    return slide.value.tabs.map(function(tab) {
      const title = tab.value.title.split(' ').join('-').replace(/'/g, '').toLocaleLowerCase();
      if (tabtype === title) {
        const half = Math.ceil(tab.value.body.length / 2);
        const secondHalf = tab.value.body.slice(-half);
        return secondHalf
          .map(function(paragraph) {
            return paragraph.value;
          })
          .join('');
      }
    });
  }

  function loadTableCell(tableBody) {
    return tableBody.map(function(trow) {
      return (
        <tr className={getRowClassName(trow)}>
          {
            trow.map(function(cell, index) {
              return (<td className={getClassName(cell, index)}>{cell}</td>);
            })
          }
        </tr>
      );
    });
  }

  function loadBody() {
    return slide.value.tabs.map(function(tab) {
      const title = tab.value.title.split(' ').join('-').replace(/'/g, '').toLocaleLowerCase();
      if (tabtype === title) {
        if (tab.value.body.length > 1) {
          return (
            <>
              <div className="cell medium-6">
                <div dangerouslySetInnerHTML={{ __html: firstHalfBody() }} />
              </div>
              <div className="cell medium-6">
                <div dangerouslySetInnerHTML={{ __html: secondHalfBody() }} />
              </div>
            </>
          );
        }

        const content = tab.value.body[0];

        if (content.type === 'table') {
          const tableData = content.value;
          const theader = tableData.first_row_is_table_header ? tableData.data[0] : [];
          const tbody = tableData.first_row_is_table_header
            ? tableData.data.slice(1) : tableData.data;

          return (
            <div className="cell">
              <table>
                <tbody>
                  <tr className="table-title">
                    {theader.map(function(paragraph, index) {
                      return (<td className={getClassName(paragraph, index)}>{paragraph}</td>);
                    })}
                  </tr>
                  { loadTableCell(tbody) }
                </tbody>
              </table>
            </div>
          );
        }
      }
    });
  }

  return (
    <div className="financials">
      <div className="grid-container">
        <div className="grid-x grid-margin-x">
          <div className="cell">
            <h1>{slide.value.title}</h1>
          </div>
        </div>
        <div className="grid-x grid-margin-x">
          <div className="cell financials-container">
            <div className="grid-x grid-margin-x">
              <div className="cell">
                <div className="financials-menu">
                  {loadTabs()}
                  <div className="download-button">
                    <a
                      href="https://cigionline.org/sites/default/files/annual-reports/2020_CIGI_FS_Final.pdf"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <svg
                        viewBox="0 0 512 512"
                        xmlns="http://www.w3.org/2000/svg"
                        role="img"
                        focusable="false"
                        aria-hidden="true"
                        data-icon="download"
                        data-prefix="fal"
                        className="svg-inline--fa fa-download fa-w-16 fa-lg"
                      >
                        <path
                          fill="currentColor"
                          d="M452 432c0 11-9 20-20 20s-20-9-20-20 9-20 20-20 20 9 20 20zm-84-20c-11 0-20 9-20 20s9 20 20 20 20-9 20-20-9-20-20-20zm144-48v104c0 24.3-19.7 44-44 44H44c-24.3 0-44-19.7-44-44V364c0-24.3 19.7-44 44-44h99.4L87 263.6c-25.2-25.2-7.3-68.3 28.3-68.3H168V40c0-22.1 17.9-40 40-40h96c22.1 0 40 17.9 40 40v155.3h52.7c35.6 0 53.4 43.1 28.3 68.3L368.6 320H468c24.3 0 44 19.7 44 44zm-261.7 17.7c3.1 3.1 8.2 3.1 11.3 0L402.3 241c5-5 1.5-13.7-5.7-13.7H312V40c0-4.4-3.6-8-8-8h-96c-4.4 0-8 3.6-8 8v187.3h-84.7c-7.1 0-10.7 8.6-5.7 13.7l140.7 140.7zM480 364c0-6.6-5.4-12-12-12H336.6l-52.3 52.3c-15.6 15.6-41 15.6-56.6 0L175.4 352H44c-6.6 0-12 5.4-12 12v104c0 6.6 5.4 12 12 12h424c6.6 0 12-5.4 12-12V364z"
                        />
                      </svg>
                      <span className="underline">Download PDF</span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
            <div className="liquid-container" style={{}}>
              <div className="liquid-child" style={{ top: 0, left: 0 }}>
                <div className="grid-x grid-margin-x financials-content">
                  {loadBody()}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Financials;
