import 'regenerator-runtime/runtime';
import React, { useEffect, useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useParams,
  Navigate,
  useNavigate,
  useLocation,
} from 'react-router-dom';
import '../../css/components/AnnualReportSlide.scss';

const fetchSlides = async (annualReportId) => {
  const response = await fetch(
    `/api/v2/annual_report_slide/?child_of=${annualReportId}&fields=slide_title,slide_content`,
  );
  const data = await response.json();
  console.log(data);
  const modifiedData = data.items.map((slide) => ({
    ...slide,
    slug: slide.meta.slug,
  }));

  return data.items.map((slide) => ({
    ...slide,
    slug: slide.meta.slug,
  }));
};

const Slide = ({ slides, basePath }) => {
  let { slug } = useParams();
  const navigate = useNavigate();

  if (!slides || slides.length === 0) {
    return <div>Loading slides...</div>;
  }

  const currentIndex = slides.findIndex((slide) => slide.slug === slug);

  if (currentIndex === -1) {
    return <Navigate to={`/${slides[0].slug}`} replace />;
  }

  const prevSlide = currentIndex > 0 ? slides[currentIndex - 1] : null;
  const nextSlide =
    currentIndex < slides.length - 1 ? slides[currentIndex + 1] : null;

  return (
    <div className="annual-report-slide">
      <div>{slides[currentIndex].id}</div>
      <h1>{slides[currentIndex].slide_title}</h1>
      <div
        dangerouslySetInnerHTML={{ __html: slides[currentIndex].slide_content }}
      />

      <div>
        <button
          onClick={() => navigate(`${basePath}/${prevSlide.slug}`)}
          disabled={!prevSlide}
        >
          Previous
        </button>

        <button
          onClick={() => navigate(`${basePath}/${nextSlide.slug}`)}
          disabled={!nextSlide}
        >
          Next
        </button>
      </div>
    </div>
  );
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
        element={<Slide slides={slides} basePath={basePath} />}
      />
      <Route
        path="*"
        element={<Navigate to={`${basePath}/${slides[0].slug}`} />}
      />
    </Routes>
  );
};

const App = ({ annualReportSPAId, basePath }) => {
  return (
    <Router>
      <AnnualReport annualReportId={annualReportSPAId} basePath={basePath} />
    </Router>
  );
};

export default App;
