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

  useEffect(() => {
    if (!subSlug && tabs.length > 0) {
      const tabSlug =
        lang === 'fr' ? `${tabs[0].slug_fr}` : `${tabs[0].slug_en}`;
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

  const t = (key) => {
    const translations = {
      currentAssets: lang === 'fr' ? 'Actifs à court terme' : 'Current Assets',
      cashAndCashEquivalents:
        lang === 'fr'
          ? 'Espèces et quasi-espèces'
          : 'Cash and Cash Equivalents',
      portfolioInvestments:
        lang === 'fr' ? 'Placements de portefeuille' : 'Portfolio Investments',
      amountsReceivable: lang === 'fr' ? 'Débiteurs' : 'Amounts Receivable',
      prepaidExpenses:
        lang === 'fr' ? "Frais payés d'avance" : 'Prepaid Expenses',
      otherAssets: lang === 'fr' ? 'Autres actifs' : 'Other Assets',
      propertyAndEquipment:
        lang === 'fr'
          ? 'Biens immobiliers et équipement'
          : 'Property and Equipment',
      leaseInducement:
        lang === 'fr' ? 'Incitatif relatif à un bail' : 'Lease Inducement',
      totalAssets: lang === 'fr' ? 'Total des actifs' : 'Total Assets',
      currentLiabilities:
        lang === 'fr' ? 'Passifs à court terme' : 'Current Liabilities',
      accountsPayable:
        lang === 'fr'
          ? 'Comptes créditeurs et charges à payer'
          : 'Accounts Payable and Accrued Liabilities',
      deferredRevenue: lang === 'fr' ? 'Revenus reportés' : 'Deferred Revenue',
      totalLiabilities: lang === 'fr' ? 'Passif total' : 'Total Liabilities',
      fundBalances: lang === 'fr' ? 'Soldes de fonds' : 'Fund Balances',
      capitalAssets:
        lang === 'fr'
          ? 'Investis en immobilisations'
          : 'Invested in Capital Assets',
      externallyRestricted:
        lang === 'fr'
          ? 'Affectations d’origine externe'
          : 'Externally Restricted',
      internallyRestricted:
        lang === 'fr'
          ? 'Affectations d’origine interne'
          : 'Internally Restricted',
      unrestricted: lang === 'fr' ? 'Non affecté' : 'Unrestricted',
      totalFundBalances:
        lang === 'fr' ? 'Solde de fonds' : 'Total Fund Balances',
      totalLiabilitiesAndFundBalances:
        lang === 'fr'
          ? 'Total du passif et des soldes des fonds'
          : 'Total Liabilities and Fund Balances',
      revenues: lang === 'fr' ? 'Produits' : 'Revenues',
      realizedInvestmentIncome:
        lang === 'fr'
          ? 'Revenu de placement réalisé'
          : 'Realized Investment Income',
      unrealizedInvestmentGains:
        lang === 'fr'
          ? 'Gain de placement non réalisé'
          : 'Unrealized Investment Gains',
      other: lang === 'fr' ? 'Autres' : 'Other',
      governmentAndOtherGrants:
        lang === 'fr'
          ? 'Subventions (gouvernementales et autres)'
          : 'Government and Other Grants',
      expenses: lang === 'fr' ? 'Charges' : 'Expenses',
      researchAndConferences:
        lang === 'fr' ? 'Recherche et conférences' : 'Research and Conferences',
      amortization: lang === 'fr' ? 'Amortissement' : 'Amortization',
      administration: lang === 'fr' ? 'Administration' : 'Administration',
      facilities: lang === 'fr' ? 'Installations' : 'Facilities',
      technicalSupport:
        lang === 'fr' ? 'Soutien technique' : 'Technical Support',
      excessOfExpensesOverRevenues:
        lang === 'fr'
          ? 'Excédent des charges sur les produits'
          : 'Excess of Expenses Over Revenues',
      fundBalancesBeginningOfYear:
        lang === 'fr'
          ? 'Solde des fonds au début de l’exercice'
          : 'Fund Balances, Beginning of Year',
      fundBalancesEndOfYear:
        lang === 'fr'
          ? 'Solde des fonds à la fin de l’exercice'
          : 'Fund Balances, End of Year',
    };
    return translations[key] || key;
  };

  const totalsCurrent = activeTab?.year_current || {};
  const totalsPrevious = activeTab?.year_previous || {};

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
        </div>
        <div className="container financials-container">
          <div className="row">
            <div className="col">
              <div className="financials-menu">
                {tabs.map((tab, idx) => {
                  const tabSlug = lang === 'fr' ? tab.slug_fr : tab.slug_en;
                  const isActive = tabSlug === activeSlug;
                  const tabTitle = lang === 'fr' ? tab.title_fr : tab.title_en;
                  const to = `${base}/${encodeURIComponent(
                    tabSlug,
                  )}${search}${hash}`;
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

                {slide.slide_content.pdf && (
                  <div className="download-button ms-3">
                    <a
                      href={slide.slide_content.pdf}
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
                )}
              </div>
            </div>
          </div>

          <div key={subSlug} className="financials-content row">
            {activeTab?.slug_en === 'auditors-report' &&
              activeTab.columns.map((col, idx) => (
                <div key={idx} className="col-12 col-md-6">
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
                        <td
                          className="text-col"
                          dangerouslySetInnerHTML={{
                            __html:
                              lang === 'fr'
                                ? activeTab.description_fr
                                : activeTab.description_en,
                          }}
                          aria-label="Financial Statement Title"
                        />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {activeTab.year_current.year_label}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {activeTab.year_previous.year_label}
                        </td>
                      </tr>
                      <tr className="table-subtitle">
                        <td className="text-col">{t('currentAssets')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('cashAndCashEquivalents')}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsCurrent?.cash_and_cash_equivalents}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsPrevious?.cash_and_cash_equivalents}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('portfolioInvestments')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.portfolio_investments}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.portfolio_investments}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('amountsReceivable')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.amounts_receivable}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.amounts_receivable}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('prepaidExpenses')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.prepaid_expenses}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.prepaid_expenses}
                        </td>
                      </tr>
                      <tr className="table-subtotal">
                        <td className="text-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.current_assets_subtotal}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.current_assets_subtotal}
                        </td>
                      </tr>
                      <tr className="table-subtitle">
                        <td className="text-col">{t('otherAssets')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('propertyAndEquipment')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.property_and_equipment}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.property_and_equipment}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('leaseInducement')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.lease_inducement}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.lease_inducement}
                        </td>
                      </tr>
                      <tr className="table-subtotal">
                        <td className="text-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.other_assets_subtotal}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.other_assets_subtotal}
                        </td>
                      </tr>
                      <tr className="table-total">
                        <td className="text-col">{t('totalAssets')}</td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsCurrent?.total_assets}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsPrevious?.total_assets}
                        </td>
                      </tr>
                      <tr className="table-subtitle">
                        <td className="text-col">{t('currentLiabilities')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('accountsPayable')}</td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {
                            totalsCurrent?.accounts_payable_and_accrued_liabilities
                          }
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {
                            totalsPrevious?.accounts_payable_and_accrued_liabilities
                          }
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('deferredRevenue')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.deferred_revenue}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.deferred_revenue}
                        </td>
                      </tr>
                      <tr className="table-subtotal">
                        <td className="text-col">{t('totalLiabilities')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.total_liabilities}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.total_liabilities}
                        </td>
                      </tr>
                      <tr className="table-subtitle">
                        <td className="text-col">{t('fundBalances')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('capitalAssets')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.invested_in_capital_assets}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.invested_in_capital_assets}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('externallyRestricted')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.externally_restricted}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.externally_restricted}
                        </td>
                      </tr>
                      {(totalsCurrent?.internally_restricted ||
                        totalsPrevious?.internallyRestricted) && (
                        <tr className="table-line-entry">
                          <td className="text-col">
                            {t('internallyRestricted')}
                          </td>
                          <td
                            className="num-col dollar-sign"
                            aria-label="blank cell"
                          />
                          <td className="num-col">
                            {totalsCurrent?.internally_restricted}
                          </td>
                          <td
                            className="num-col dollar-sign"
                            aria-label="blank cell"
                          />
                          <td className="num-col">
                            {totalsPrevious?.internally_restricted}
                          </td>
                        </tr>
                      )}
                      <tr className="table-line-entry">
                        <td className="text-col">{t('unrestricted')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.unrestricted}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.unrestricted}
                        </td>
                      </tr>
                      <tr className="table-subtotal">
                        <td className="text-col">{t('totalFundBalances')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent?.total_fund_balances}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious?.total_fund_balances}
                        </td>
                      </tr>
                      <tr className="table-final-total">
                        <td className="text-col">
                          {t('totalLiabilitiesAndFundBalances')}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsCurrent?.total_liabilities_and_fund_balances}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsPrevious?.total_liabilities_and_fund_balances}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab?.slug_en ===
              'summarized-statement-of-revenues-and-expenses-and-changes-in-fund-balances' && (
              <div className="col financials-content">
                <div className="cell">
                  <table>
                    <tbody>
                      <tr className="table-title">
                        <td
                          className="text-col"
                          dangerouslySetInnerHTML={{
                            __html:
                              lang === 'fr'
                                ? activeTab.description_fr
                                : activeTab.description_en,
                          }}
                          aria-label="Financial Statement Title"
                        />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {activeTab.year_current.year_label}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {activeTab.year_previous.year_label}
                        </td>
                      </tr>
                      <tr className="table-subtitle">
                        <td className="text-col">{t('revenues')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('realizedInvestmentIncome')}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsCurrent.realized_investment_income}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsPrevious.realized_investment_income}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('unrealizedInvestmentGains')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.unrealizedInvestmentGains}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.unrealizedInvestmentGains}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('other')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">{totalsCurrent.other}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">{totalsPrevious.other}</td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('governmentAndOtherGrants')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.government_and_other_grants}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.government_and_other_grants}
                        </td>
                      </tr>
                      <tr className="table-subtotal">
                        <td className="text-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.total_revenue}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.total_revenue}
                        </td>
                      </tr>
                      <tr className="table-subtitle">
                        <td className="text-col">{t('expenses')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col" aria-label="blank cell" />
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">
                          {t('researchAndConferences')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.research_and_conferences}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.research_and_conferences}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('amortization')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.amortization}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.amortization}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('administration')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.administration}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.administration}
                        </td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('facilities')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">{totalsCurrent.facilities}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">{totalsPrevious.facilities}</td>
                      </tr>
                      <tr className="table-line-entry">
                        <td className="text-col">{t('technicalSupport')}</td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.technical_support}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.technical_support}
                        </td>
                      </tr>
                      <tr className="table-subtotal">
                        <td className="text-col" aria-label="blank cell" />
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.total_expenses}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.total_expenses}
                        </td>
                      </tr>
                      <tr className="table-subtotal no-bottom-border">
                        <td className="">
                          {t('excessOfExpensesOverRevenues')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.excess_of_expenses_over_revenue}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.excess_of_expenses_over_revenue}
                        </td>
                      </tr>
                      <tr className="table-fund-balances">
                        <td className="text-col">
                          {t('fundBalancesBeginningOfYear')}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsCurrent.fund_balances_beginning_of_year}
                        </td>
                        <td
                          className="num-col dollar-sign"
                          aria-label="blank cell"
                        />
                        <td className="num-col">
                          {totalsPrevious.fund_balances_beginning_of_year}
                        </td>
                      </tr>
                      <tr className="table-final-total">
                        <td className="text-col">
                          {t('fundBalancesEndOfYear')}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsCurrent.fund_balances_end_of_year}
                        </td>
                        <td className="num-col dollar-sign">$</td>
                        <td className="num-col">
                          {totalsPrevious.fund_balances_end_of_year}
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
  );
}

AnnualReportsFinancialsSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
};

export default AnnualReportsFinancialsSlide;
