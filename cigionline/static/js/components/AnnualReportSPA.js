import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, Router } from 'react-router-dom';
import '../../css/components/AnnualReportSlide.scss';
import AnnualReportSlide from './AnnualReportSlide';
import Loader from './Loader';

const fetchSlides = async (annualReportSPAId) => {
  const response = await fetch(`/api/annual-report/${annualReportSPAId}/slides/`);
  try {
    const data = await response.json();
    return data.slides;
  } catch (error) {
    console.error('Error fetching slides:', error);
    return [];
  }
};

const AnnualReportSPA = ({ annualReportSPAId, basePath }) => {
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
    return (
      <div className="loading-screen">
        <Loader />
      </div>
    );
  }

  if (slides.length === 0) {
    return <div>No slides found.</div>;
  }

  return (
    <Router>
      <Routes>
        <Route
          path={`${basePath}/:slug`}
          element={<AnnualReportSlide slides={slides} basePath={basePath} isLoading={loading} />}
        />
        <Route
          path="*"
          element={<Navigate to={`${basePath}/${slides[0].slug}`} />}
        />
      </Routes>
    </Router>
  );
};

AnnualReportSPA.propTypes = {
  annualReportSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default AnnualReportSPA;
