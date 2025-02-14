import 'regenerator-runtime/runtime';
import React, { useEffect, useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useParams,
  Navigate,
} from 'react-router-dom';

const fetchSlides = async (annualReportId) => {
  const response = await fetch(
    `/api/v2/annual_report_slide/?child_of=${annualReportId}`,
  );
  const data = await response.json();
  console.log(data);
  return data.items;
};

const Slide = ({ slides }) => {
  let { slideIndex } = useParams();
  const slide = slides[slideIndex] || null;

  if (!slide) return <Navigate to="/not-found" />;
  return (
    <div>
      <h1>{slide.slide_title}</h1>
      <div dangerouslySetInnerHTML={{ __html: slide.title }} />
    </div>
  );
};

const AnnualReport = ({ annualReportId }) => {
  const [slides, setSlides] = useState([]);

  useEffect(() => {
    fetchSlides(annualReportId).then(setSlides);
  }, [annualReportId]);

  return (
    <Routes>
      {slides.map((_, index) => (
        <Route
          key={index}
          path={`/${index}`}
          element={<Slide slides={slides} />}
        />
      ))}
      <Route path="*" element={<Navigate to={`/annual-reports/${annualReportId}/${annualReportId}`} />} />
    </Routes>
  );
};

const App = ({ annualReportSPAId }) => {
  return (
    <Router>
      <AnnualReport annualReportId={annualReportSPAId} />
    </Router>
  );
};

export default App;
