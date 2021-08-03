import React, { Fragment } from 'react';

const Financials = ({ slide }) => ( // eslint-disable-line no-unused-vars
  <div className="financials">
    <div className="grid-container">
      <div className="grid-x grid-margin-x">
        <div className="cell">
          <h1>Financials</h1>
        </div>
      </div>
      <div className="grid-x grid-margin-x">
        <div className="cell financials-container">
          <div className="grid-x grid-margin-x">
            <div className="cell">
              <div className="financials-menu">
                Auditor’s Report
                <span className="menu-break">/</span>
                <a href="/interactives/2020annualreport/en/financials/summarized-statement-of-financial-position">
                  <span className="underline">
                    Summarized Statement of Financial Position
                  </span>
                </a>
                <span className="menu-break">/</span>
                <a href="/interactives/2020annualreport/en/financials/summarized-statement-of-revenues-and-expenses-and-changes-in-fund-balances">
                  <span className="underline">
                    Summarized Statement of Revenues and Expenses and Changes
                    in Fund Balances
                  </span>
                </a>
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
                <div className="cell medium-6">
                  <h4>
                    Report of the Independent Auditors on the Summary
                    Financial Statements
                  </h4>
                  <p>
                    To the Directors of The Centre for International
                    Governance Innovation,
                  </p>
                  <h4>Opinion</h4>
                  <p>
                    The summary financial statements, which comprise the
                    summary statement of financial position as at July 31,
                    2020, the summary statement of revenues and expenses and
                    changes in fund balances for the year then ended, are
                    derived from the audited financial statements of The
                    Centre for International Governance Innovation (the
                    “Organization”) as at and for the year ended July 31,
                    2020.
                  </p>
                  <p>
                    In our opinion, the accompanying summary financial
                    statements are a fair summary of the audited financial
                    statements in accordance with the basis developed by
                    management, which includes removing the statement of cash
                    flows, retaining major subtotals, totals and comparative
                    information, and retaining the information from the
                    audited financial statements dealing with matters having a
                    pervasive or otherwise significant effect on the summary
                    financial statements.
                  </p>
                  <h4>Summary Financial Statements</h4>
                  <p>
                    The summary financial statements do not contain all the
                    disclosures required by Canadian accounting standards for
                    not-for-profit organizations. Reading the summary
                    financial statements, therefore, is not a substitute for
                    reading the audited financial statements of the
                    Organization.
                  </p>
                </div>
                <div className="cell medium-6">
                  <>
                    <h4>
                      The Audited Financial Statements and Our Report Thereon
                    </h4>
                    <p>
                      We expressed an unmodified audit opinion on the audited
                      financial statements in our report dated November 27,
                      2020.
                    </p>
                    <h4>
                      Management’s Responsibility for the Summary Financial
                      Statements
                    </h4>
                    <p>
                      Management is responsible for the preparation of the
                      summary financial statements on a basis developed by
                      management, which includes removing the statement of
                      cash flows, retaining major subtotals, totals and
                      comparative information, and retaining the information
                      from the audited financial statements dealing with
                      matters having a pervasive or otherwise significant
                      effect on the summary financial statements.
                    </p>
                    <h4>Auditor’s Responsibility</h4>
                    <p>
                      Our responsibility is to express an opinion on whether
                      the summary financial statements are a fair summary of
                      the audited financial statements based on our
                      procedures, which were conducted in accordance with
                      Canadian Auditing Standard (CAS) 810, Engagements to
                      Report on Summary Financial Statements.
                    </p>
                    <h4>Other matter</h4>
                    <p>
                      The audited financial statements of the Organization are
                      available upon request by contacting the Organization.
                    </p>
                    <div className="auditor-signature">
                      <>
                        <img
                          src="https://www.cigionline.org/interactives/2019annualreport/static/template/slides/auditors-sig.png"
                          alt="Auditor’s signature"
                          width="105"
                          height="18"
                        />
                        <p>
                          Chartered Professional Accountants
                          <br />
                          Licensed Public Accountants
                          <br />
                          Toronto, Ontario, November 27, 2020
                        </p>
                      </>
                    </div>
                  </>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default Financials;
