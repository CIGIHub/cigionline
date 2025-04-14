import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import '../../../css/components/AnnualReportSPA.scss';
import StrategicPlanSlide from './StrategicPlanSlide';
import Loader from '../Loader';

const fetchSlides = async (strategicPlanSPAId) => {
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

const BackgroundVideoPreloader = ({ slides }) => {
  useEffect(() => {
    slides.forEach((slide) => {
      if (!slide.background_video) return;

      const video = document.createElement('video');
      video.src = slide.background_video;
      video.muted = true;
      video.playsInline = true;
      video.preload = 'auto';
      video.setAttribute('data-slug', slide.slug);
      video.style.position = 'absolute';
      video.style.width = '1px';
      video.style.height = '1px';
      video.style.zIndex = -100;
      video.style.pointerEvents = 'none';
      video.style.opacity = 0;

      document.body.appendChild(video);
    });
  }, [slides]);

  return null;
};

const StrategicPlan = ({ strategicPlanSPAId, basePath }) => {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSlides(strategicPlanSPAId)
      .then((data) => {
        setSlides(data);
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
      <BackgroundVideoPreloader slides={slides} />
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
