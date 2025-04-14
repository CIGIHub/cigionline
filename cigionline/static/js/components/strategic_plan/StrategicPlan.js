import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import '../../../css/components/AnnualReportSPA.scss';
import StrategicPlanSlide from './StrategicPlanSlide';
import Loader from '../Loader';
import usePreloadSlideAssets from './usePreloadSlideAssets';

const fetchSlides = async (strategicPlanSPAId, slides) => {
  const response = await fetch(
    `/api/strategic_plan/${strategicPlanSPAId}/slides/`,
  );
  try {
    const data = await response.json();
    return data.slides;
  } catch (error) {
    console.error('Error fetching slides:', error);
    return [];
  }
};

const StrategicPlan = ({ strategicPlanSPAId, basePath }) => {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSlides(strategicPlanSPAId)
      .then((data) => {
        setSlides(data);
        usePreloadSlideAssets(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [strategicPlanSPAId]);

  if (loading) {
    return <Loader isLoading={loading} />;
  }

  if (!slides) {
    return <div>No slides found.</div>;
  }

  return (
    <>
      <Routes>
        <Route
          path={`${basePath}/:slug`}
          element={<StrategicPlanSlide slides={slides} basePath={basePath} />}
        />
        <Route
          path="*"
          element={<Navigate to={`${basePath}/${slides[0]?.slug || ''}`} />}
        />
      </Routes>
    </>
  );
};

StrategicPlan.propTypes = {
  strategicPlanSPAId: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
};

export default StrategicPlan;
