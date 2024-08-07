/* eslint-disable jsx-a11y/no-static-element-interactions */
/* eslint-disable jsx-a11y/click-events-have-key-events */
/* eslint-disable react/no-danger */
/* eslint-disable react/prop-types */
import React, { useState } from 'react';
import SwiperCore from 'swiper';
import { Navigation, Pagination } from 'swiper/modules'; // eslint-disable-line import/no-unresolved
import { Swiper, SwiperSlide } from 'swiper/react'; // eslint-disable-line import/no-unresolved
import 'swiper/swiper-bundle.css';

import '../../css/components/TwentiethPageSlide3Content.scss';

SwiperCore.use([Navigation, Pagination]);

const TwentiethPageSlide3Content = ({ slide }) => {
  slide.timeline.sort((a, b) => Number(a.year) - Number(b.year));
  const years = slide.timeline.map((year) => year.year);
  const [currentYear, setCurrentYear] = useState(years[0]);
  const [swiper, setSwiper] = useState(null);
  const [swiperModal, setSwiperModal] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const setYear = (year) => {
    setCurrentYear(year);
    swiper.slideTo(years.indexOf(year));
  };

  function handleSlideClick() {
    if (screen.width > 768) {
      swiperModal.slideTo(swiper.clickedIndex, 0);
      setShowModal(true);
      document.getElementById('slides-nav-arrows').classList.add('hidden');
    }
  }

  function handleCloseModal(e) {
    if (
      !(
        e.target.classList.contains('fa-angle-right')
        || e.target.classList.contains('fa-angle-left')
      )
    ) {
      setShowModal(false);
      document.getElementById('slides-nav-arrows').classList.remove('hidden');
    }
  }

  function highlightYear(year, index) {
    if (screen.width > 768) {
      return index === years.indexOf(currentYear)
        || index === years.indexOf(currentYear) + 1
        || (index === year.length - 2
        && years.indexOf(currentYear) === years.length - 1)
        ? 'active'
        : '';
    }
    return index === years.indexOf(currentYear) ? 'active' : '';
  }

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
            <ul className="timeline-nav">
              {years.map((year, index) => (
                <li className={highlightYear(year, index)} key={year}>
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
                slidesPerView={1}
                spaceBetween={30}
                breakpoints={{
                  768: {
                    slidesPerView: 2,
                    spaceBetween: 30,
                  },
                }}
                navigation={{
                  nextEl: '.swiper-button-next',
                  prevEl: '.swiper-button-prev',
                  disabledClass: 'swiper-button-disabled',
                }}
                className="mySwiper"
                onSlideChange={({ activeIndex }) => setCurrentYear(years[activeIndex])}
                onSwiper={setSwiper}
                watchSlidesProgress
              >
                <div className="swiper-button-next">
                  <i className="fal fa-angle-right" />
                </div>
                <div className="swiper-button-prev">
                  <i className="fal fa-angle-left" />
                </div>
                {slide.timeline.map((year) => (
                  <SwiperSlide key={year.year} onClick={handleSlideClick}>
                    <div className="timeline-slide" key={year.year}>
                      <div className="img-wrapper align-items-center">
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
              <div
                className={`modal-overlay ${showModal && 'modal-active'}`}
                onClick={handleCloseModal}
              >
                <Swiper
                  slidesPerView={1}
                  centeredSlides
                  navigation={{
                    nextEl: '.swiper-modal-button-next',
                    prevEl: '.swiper-modal-button-prev',
                    disabledClass: 'swiper-modal-button-disabled',
                  }}
                  className="mySwiper"
                  onSwiper={setSwiperModal}
                >
                  <div className="swiper-modal-button-next">
                    <i className="fal fa-angle-right" />
                  </div>
                  <div className="swiper-modal-button-prev">
                    <i className="fal fa-angle-left" />
                  </div>
                  {slide.timeline.map((year) => (
                    <SwiperSlide key={year.year}>
                      <div
                        className="timeline-slide-modal d-flex flex-column"
                        key={year.year}
                      >
                        <div className="img-wrapper d-flex align-items-center">
                          <img src={year.image} alt="" />
                        </div>
                        <div className="timeline-text">
                          <h2 className="timeline-year underline">
                            {year.year}
                          </h2>
                          <div
                            className="timeline-body"
                            dangerouslySetInnerHTML={{ __html: year.body }}
                          />
                        </div>
                        <button
                          type="button"
                          className="close-modal"
                          onClick={handleCloseModal}
                        >
                          <i className="fal fa-times-square" />
                        </button>
                      </div>
                    </SwiperSlide>
                  ))}
                </Swiper>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TwentiethPageSlide3Content;
