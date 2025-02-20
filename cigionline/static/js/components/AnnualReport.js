import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AnnualReportSlide from './AnnualReportSlide';

const fetchSlides = async (annualReportId) => {
  const response = await fetch(`/api/annual-report/${annualReportId}/slides/`);
  try {
    const data = await response.json();
    return data.slides;
  } catch (error) {
    console.error('Error fetching slides:', error);
    return [];
  }
};

const AnnualReport = ({ annualReportId, basePath }) => {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSlides(annualReportId)
      .then((data) => {
        setSlides(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [annualReportId]);

  if (loading) {
    return <div>Loading slides...</div>;
  }

  if (slides.length === 0) {
    return <div>No slides found.</div>;
  }

  return (
    <Routes>
      <Route
        path={`${basePath}/:slug`}
        element={<AnnualReportSlide slides={slides} basePath={basePath} />}
      />
      <Route
        path="*"
        element={<Navigate to={`${basePath}/${slides[0].slug}`} />}
      />
    </Routes>
  );
};

AnnualReport.propTypes = {
  annualReportId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReport;
