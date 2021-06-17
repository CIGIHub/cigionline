import React, { useRef, useState } from 'react';
import PropTypes from 'prop-types';

import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/swiper.min.css';
import 'swiper/components/pagination/pagination.min.css';

import SwiperCore, { Navigation, Pagination } from 'swiper/core';

import '../../css/components/TwentiethPageSlide3Content.scss';

SwiperCore.use([Navigation, Pagination]);

const TwentiethPageSlide3Content = ({ slide }) => {
  slide.timeline.sort((a, b) => Number(a.year) - Number(b.year));
  const years = slide.timeline.map((year) => year.year);
  const [currentYear, setCurrentYear] = useState(years[0]);

  const setYear = (year) => {
    setCurrentYear(year);
  };
  return (
    <div className="col slide-3">
      {slide.title && <h1>{slide.title}</h1>}
      <h2>Current Year: {currentYear}</h2>
      <ul>
        {slide.timeline.map((year) => (
          <li key={year.year}>
            <button type="button" onClick={() => setYear(year.year)}>
              {year.year}
            </button>
          </li>
        ))}
      </ul>
      {slide.timeline && (
        <Swiper
          slidesPerView={4}
          centeredSlides
          spaceBetween={30}
          pagination={{
            clickable: true,
          }}
          navigation
          className="mySwiper"
        >
          {slide.timeline.map((year) => (
            <SwiperSlide key={year.year}>
              <div className="timeline-slide" key={year.year}>
                <h2 className="timeline-year">{year.year}</h2>
                <p
                  className="timeline-body"
                  dangerouslySetInnerHTML={{ __html: year.body }}
                />
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
      )}
    </div>
  );
};
TwentiethPageSlide3Content.propTypes = {};

export default TwentiethPageSlide3Content;
