import React, { useRef, useState } from 'react';
import PropTypes from 'prop-types';

import SwiperCore, { Navigation, Pagination } from 'swiper/core';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/swiper.scss';

import '../../css/components/TwentiethPageSlide3Content.scss';

SwiperCore.use([Navigation, Pagination]);

const TwentiethPageSlide3Content = ({ slide }) => {
  slide.timeline.sort((a, b) => Number(a.year) - Number(b.year));
  const years = slide.timeline.map((year) => year.year);
  const [currentYear, setCurrentYear] = useState(years[0]);
  const [swiper, setSwiper] = useState(null);

  const setYear = (year) => {
    setCurrentYear(year);
    swiper.slideTo(years.indexOf(year));
  };
  return (
    <div className="slide-content">
      <div className="container">
        <div className="row justify-content-center text-center">
          <div className="col-md-10 col-lg-8 slide-3">
            {slide.title && <h1>{slide.title}</h1>}
          </div>
        </div>
        <div className="row justify-content-center text-center">
          <div className="col-md-8 col-lg-6">
            <ul className="timeline-nav d-flex">
              {years.map((year, index) => (
                <li
                  className={
                    index === years.indexOf(currentYear) ||
                    index === years.indexOf(currentYear) + 1 ||
                    (index === year.length - 2 &&
                      years.indexOf(currentYear) === years.length - 1)
                      ? 'active'
                      : ''
                  }
                  key={year}
                >
                  <button type="button" onClick={() => setYear(year)}>
                    {year}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      {slide.timeline && (
        <div className="container">
          <div className="row justify-content-center text-center">
            <div className="col">
              <Swiper
                slidesPerView={2}
                spaceBetween={30}
                navigation={{
                  nextEl: '.swiper-button-next',
                  prevEl: '.swiper-button-prev',
                  disabledClass: 'swiper-button-disabled',
                }}
                className="mySwiper"
                onSlideChange={({ activeIndex }) =>
                  setCurrentYear(years[activeIndex])
                }
                onSwiper={setSwiper}
              >
                <div className="swiper-button-next">
                  <i className="fal fa-angle-right" />
                </div>
                <div className="swiper-button-prev">
                  <i className="fal fa-angle-left" />
                </div>
                {slide.timeline.map((year) => (
                  <SwiperSlide key={year.year}>
                    <div className="timeline-slide d-flex" key={year.year}>
                      <div className="img-wrapper d-flex align-items-center">
                        <img src={year.image} alt="" />
                      </div>
                      <div className="timeline-text">
                        <h2 className="timeline-year">{year.year}</h2>
                        <div
                          className="timeline-body"
                          dangerouslySetInnerHTML={{ __html: year.body }}
                        />
                      </div>
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
TwentiethPageSlide3Content.propTypes = {};

export default TwentiethPageSlide3Content;
