import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AnnualReportSlide from './AnnualReportSlide';
import Loader from '../Loader';

const fetchSlides = async (annualReportSPAId) => {
  const response = await fetch(
    `/api/annual-report/${annualReportSPAId}/slides/`,
  );
  try {
    const data = await response.json();
    return data.slides;
  } catch (error) {
    console.error('Error fetching slides:', error);
    return [];
  }
};

function AnnualReport({ annualReportSPAId, basePath }) {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSlides(annualReportSPAId)
      .then((data) => {
        setSlides(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [annualReportSPAId]);

  if (loading) {
    return <Loader isLoading={loading} />;
  }

  if (slides.length === 0) {
    return <div>No slides found.</div>;
  }

  return (
    <Routes>
      <Route
        path={`${basePath}/:lang?/:slug/:subSlug?`}
        element={<AnnualReportSlide slides={slides} basePath={basePath} />}
      />
      <Route
        path="*"
        element={<Navigate to={`${basePath}/en/${slides[0].slug || ''}/`} />}
      />
    </Routes>
  );
}

AnnualReport.propTypes = {
  annualReportSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReport;
