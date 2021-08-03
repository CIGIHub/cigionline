import React from 'react';

import HomeSlide from './HomeSlide';
import TableOfContents from './TableOfContents';
import MessageSlide from './MessageSlide';
import ContentSlide from './ContentSlide';
import OutputsAndActivities from './OutputsAndActivities';
import Financials from './Financials';
import Timeline from './Timeline';

const Slide = ({
  slide, slides, contentOpacity, navigateToSlide, isOpen,
}) => {
  const getComponent = () => {
    if (slide.type === '') {
      return <HomeSlide />;
    } if (slide.type === 'summaryslidepage') {
      return (
        <TableOfContents
          slide={slide}
          slides={slides}
          isOpen={isOpen}
          contentOpacity={contentOpacity}
          navigateToSlide={navigateToSlide}
        />
      );
    } if (slide.type === 'messageslidepage') {
      return <MessageSlide slide={slide} contentOpacity={contentOpacity} />;
    } if (slide.type === 'contentslidepage') {
      return <ContentSlide slide={slide} contentOpacity={contentOpacity} />;
    } if (slide.type === 'outputsandactivitiesslidepage') {
      return (
        <OutputsAndActivities slide={slide} contentOpacity={contentOpacity} />
      );
    } if (slide.type === 'timelineslidepage') {
      return <Timeline slide={slide} contentOpacity={contentOpacity} />;
    } if (slide.type === 'tabbedslidepage') {
      return <Financials slide={slide} contentOpacity={contentOpacity} />;
    }
    return <HomeSlide />;
  };

  return (
    <>
      {getComponent()}
    </>

  );
};

export default Slide;
