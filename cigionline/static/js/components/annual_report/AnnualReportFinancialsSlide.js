import PropTypes from 'prop-types';
import React, { useMemo, useEffect } from 'react';
import { Link, useParams, useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '../../../css/components/annual_reports/AnnualReportsFinancialsSlide.scss';
import { faDownload } from '@fortawesome/pro-light-svg-icons';

function AnnualReportsFinancialsSlide({ slide, lang }) {
  const navigate = useNavigate();
  const { subSlug } = useParams();
  const { pathname, search, hash } = useLocation();
  const tabs = useMemo(() => slide?.slide_content.tabs || [], [slide]);

  const base = React.useMemo(() => {
    const trimmed = pathname.replace(/\/+$/, '');
    return subSlug ? trimmed.replace(/\/[^/]+$/, '') : trimmed;
  }, [pathname, subSlug]);

  console.log(slide);
  console.log(tabs);

  useEffect(() => {
    if (!subSlug && tabs.length > 0) {
      const tabSlug = lang === 'fr' ? `${tabs[0].slug_fr}/fr` : tabs[0].slug_en;
      navigate(tabSlug, { replace: true });
    }
  }, [subSlug, tabs, navigate]);

  const activeSlug =
    subSlug || (lang === 'fr' && tabs[0].slug_fr) || tabs[0].slug_en;
  const activeTab =
    tabs.find((t) => {
      if (lang === 'fr') {
        return t.slug_fr === activeSlug;
      }
      return t.slug_en === activeSlug;
    }) || null;

  console.log(activeSlug);
  console.log(activeTab);

  // Helper for translations (replace with your i18n solution if needed)
  const t = (key) => {
    const translations = {
      currentAssets: lang === 'fr' ? 'Actifs à court terme' : 'Current Assets',
      cashAndCashEquivalents:
        lang === 'fr' ? 'Espèces et quasi-espèces' : 'Cash and Cash Equivalents',
      portfolioInvestments:
        lang === 'fr' ? 'Placements de portefeuille' : 'Portfolio Investments',
      amountsReceivable:
        lang === 'fr' ? 'Débiteurs' : 'Amounts Receivable',
      prepaidExpenses:
        lang === 'fr' ? "Frais payés d'avance" : 'Prepaid Expenses',
      otherAssets: lang === 'fr' ? 'Autres actifs' : 'Other Assets',
      propertyAndEquipment:
        lang === 'fr' ? 'Biens immobiliers et équipement' : 'Property and Equipment',
      leaseInducement:
        lang === 'fr' ? 'Incitatif relatif à un bail' : 'Lease Inducement',
      totalAssets: lang === 'fr' ? 'Total des actifs' : 'Total Assets',
      currentLiabilities:
        lang === 'fr' ? 'Passifs à court terme' : 'Current Liabilities',
      accountsPayable:
        lang === 'fr'
          ? 'Comptes créditeurs et charges à payer'
          : 'Accounts Payable and Accrued Liabilities',
      deferredRevenue:
        lang === 'fr' ? 'Revenus reportés' : 'Deferred Revenue',
      totalLiabilities:
        lang === 'fr' ? 'Passif total' : 'Total Liabilities',
      fundBalances: lang === 'fr' ? 'Soldes de fonds' : 'Fund Balances',
      capitalAssets:
        lang === 'fr' ? 'Investis en immobilisations' : 'Invested in Capital Assets',
      externallyRestricted:
        lang === 'fr' ? 'Affectations d’origine externe' : 'Externally Restricted',
      internallyRestricted:
        lang === 'fr' ? 'Affectations d’origine interne' : 'Internally Restricted',
      unrestricted:
        lang === 'fr' ? 'Non affecté' : 'Unrestricted',
      totalFundBalances:
        lang === 'fr' ? 'Soldes de fonds' : 'Total Fund Balances',
      totalLiabilitiesAndFundBalances:
        lang === 'fr'
          ? 'Total du passif et des soldes des fonds'
          : 'Total Liabilities and Fund Balances',
    };
    return translations[key] || key;
  };

  const formatCurrency = (value) => {
    if (typeof value !== 'number') return '';
    return value.toLocaleString(lang === 'fr' ? 'fr-CA' : 'en-CA');
  };

  const totals2024 = activeTab?.year_current || {};
  const totals2023 = activeTab?.year_previous || {};

  return (
    <div className="annual-report-slide">
      <div className="background-row financials-background d-none d-md-block" />
      <div className="financials">
        <div className="container">
          <div className="row">
            <div className="col">
              <h1>{lang === 'en' ? 'Financials' : 'Financières'}</h1>
            </div>
          </div>
          <div className="row">
            <div className="col financials-container">
              <div className="row">
                <div className="col">
                  <div className="financials-menu d-flex align-items-center">
                    {tabs.map((tab, idx) => {
                      const tabSlug = lang === 'fr' ? tab.slug_fr : tab.slug_en;
                      const isActive = tabSlug === activeSlug;
                      const tabTitle =
                        lang === 'fr' ? tab.title_fr : tab.title_en;
                      const to = `${base}/${encodeURIComponent(tabSlug)}${search}${hash}`;
                      return (
                        <React.Fragment key={tabSlug}>
                          {isActive ? (
                            tabTitle
                          ) : (
                            <Link
                              to={to}
                              replace
                              className={`financials-tab-link ${
                                isActive ? 'is-active' : ''
                              }`}
                              aria-current={isActive}
                            >
                              <span className={isActive ? '' : 'underline'}>
                                {tabTitle}
                              </span>
                            </Link>
                          )}
                          {idx < tabs.length - 1 && (
                            <span className="menu-break mx-2">/</span>
                          )}
                        </React.Fragment>
                      );
                    })}

                    <div className="download-button ms-3">
                      <a
                        href={slide.downloadPdfLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="d-flex align-items-center"
                      >
                        <FontAwesomeIcon icon={faDownload} size="lg" />
                        <span className="underline ms-2">
                          {lang === 'en' ? 'Download PDF' : 'Télécharger PDF'}
                        </span>
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div key={subSlug} className="financials-content row">
                {activeTab?.slug_en === 'auditors-report' &&
                  activeTab.columns.map((col, idx) => (
                    <div key={idx} className="col col-md-6">
                      {lang === 'fr'
                        ? col.fr.map((html, hIdx) => (
                            <React.Fragment key={hIdx}>
                              {typeof html === 'string' ? (
                                <div
                                  key={hIdx}
                                  dangerouslySetInnerHTML={{ __html: html }}
                                />
                              ) : (
                                <div key={hIdx} className="auditor-signature">
                                  <img
                                    src={html.signature}
                                    alt="auditor signature"
                                    width="105"
                                    height="18"
                                  />
                                  <p
                                    dangerouslySetInnerHTML={{
                                      __html: html.signature_text,
                                    }}
                                  />
                                </div>
                              )}
                            </React.Fragment>
                          ))
                        : col.en.map((html, hIdx) => (
                            <React.Fragment key={hIdx}>
                              {typeof html === 'string' ? (
                                <div
                                  key={hIdx}
                                  dangerouslySetInnerHTML={{ __html: html }}
                                />
                              ) : (
                                <div key={hIdx} className="auditor-signature">
                                  <img
                                    src={html.signature}
                                    alt="auditor signature"
                                    width="105"
                                    height="18"
                                  />
                                  <p
                                    dangerouslySetInnerHTML={{
                                      __html: html.signature_text,
                                    }}
                                  />
                                </div>
                              )}
                            </React.Fragment>
                          ))}
                    </div>
                  ))}
                {activeTab?.slug_en ===
                  'summarized-statement-of-financial-position' && (
                  <div className="col financials-content">
                    <div className="cell">
                      <table>
                        <tbody>
                          <tr className="table-title">
                            <td className="text-col">
                              {lang === 'fr'
                                ? activeTab.title_fr
                                : activeTab.title_en}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {activeTab.year_current.year_label}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {activeTab.year_previous.year_label}
                            </td>
                          </tr>
                          <tr className="table-subtitle">
                            <td className="text-col">
                              {lang === 'fr'
                                ? 'Actifs à court terme'
                                : 'Current Assets'}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {lang === 'fr'
                                ? 'Espèces et quasi-espèces'
                                : 'Cash and Cash Equivalents'}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2024?.cash_and_cash_equivalents}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2023?.cash_and_cash_equivalents}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('portfolioInvestments')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.portfolio_investments}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.portfolio_investments}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('accountsReceivable')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.accounts_receivable}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.accounts_receivable}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">{t('prepaidExpenses')}</td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.prepaid_expenses}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.prepaid_expenses}
                            </td>
                          </tr>
                          <tr className="table-subtotal">
                            <td className="text-col" aria-label="blank cell" />
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.current_assets_subtotal}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.current_assets_subtotal}
                            </td>
                          </tr>
                          <tr className="table-subtitle">
                            <td className="text-col">{t('otherAssets')}</td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('propertyAndEquipment')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.property_and_equipment}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.property_and_equipment}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('leaseInducement')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.lease_inducement}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.lease_inducement}
                            </td>
                          </tr>
                          <tr className="table-subtotal">
                            <td className="text-col" aria-label="blank cell" />
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.other_assets_subtotal}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.other_assets_subtotal}
                            </td>
                          </tr>
                          <tr className="table-total">
                            <td className="text-col">{t('totalAssets')}</td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2024?.total_assets}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2023?.total_assets}
                            </td>
                          </tr>
                          <tr className="table-subtitle">
                            <td className="text-col">
                              {t('currentLiabilities')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('accountsPayable')}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2024?.accounts_payable_and_accrued_liabilities}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2023?.accounts_payable_and_accrued_liabilities}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('deferredRevenue')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.deferred_revenue}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.deferred_revenue}
                            </td>
                          </tr>
                          <tr className="table-subtotal">
                            <td className="text-col">
                              {t('totalLiabilities')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.total_liabilities}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.total_liabilities}
                            </td>
                          </tr>
                          <tr className="table-subtitle">
                            <td className="text-col">{t('fundBalances')}</td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col" aria-label="blank cell" />
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('capitalAssets')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.invested_in_capital_assets}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.invested_in_capital_assets}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('externallyRestricted')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.externally_restricted}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.externally_restricted}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('internallyRestricted')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.internally_restricted}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.internally_restricted}
                            </td>
                          </tr>
                          <tr className="table-line-entry">
                            <td className="text-col">
                              {t('unrestricted')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.unrestricted}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.unrestricted}
                            </td>
                          </tr>
                          <tr className="table-subtotal">
                            <td className="text-col">
                              {t('totalFundBalances')}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2024?.total_fund_balances}
                            </td>
                            <td className="num-col dollar-sign" aria-label="blank cell" />
                            <td className="num-col">
                              {totals2023?.total_fund_balances}
                            </td>
                          </tr>
                          <tr className="table-final-total">
                            <td className="text-col">
                              {t('totalLiabilitiesAndFundBalances')}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2024?.total_liabilities_and_fund_balances}
                            </td>
                            <td className="num-col dollar-sign">$</td>
                            <td className="num-col">
                              {totals2023?.total_liabilities_and_fund_balances}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

AnnualReportsFinancialsSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
};

export default AnnualReportsFinancialsSlide;
