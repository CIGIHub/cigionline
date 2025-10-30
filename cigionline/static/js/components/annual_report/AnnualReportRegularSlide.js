import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faFileLines,
  faFilm,
  faPodcast,
  faCalendarDays,
  faNewspaper,
  faUser,
  faEnvelope,
  faHeadphones,
  faMagnifyingGlass,
  faMessageLines,
  faSquarePollVertical,
} from '@fortawesome/pro-light-svg-icons';
import { faHeadphones as faHeadphonesSolid } from '@fortawesome/free-solid-svg-icons';
import { motion, AnimatePresence } from 'framer-motion';
import '../../../css/components/annual_reports/AnnualReportRegularSlide.scss';

function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) setMatches(media.matches);
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);
  return matches;
}

const variants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeInOut' },
  },
};

const contentIcons = {
  publication: faFileLines,
  opinion: faMessageLines,
  video: faFilm,
  podcast: faPodcast,
  event: faCalendarDays,
  'essay series': faNewspaper,
  media: faNewspaper,
  'news release': faNewspaper,
  experts: faUser,
  subscribe: faEnvelope,
  listen: faHeadphones,
  explore: faMagnifyingGlass,
  episode: faHeadphonesSolid,
  survey: faSquarePollVertical,
};

const customIcons = {
  research: (
    <svg
      className="svg-inline--fa"
      viewBox="0 0 250 250"
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title> copy</title>
      <g
        id="Page-1"
        stroke="none"
        strokeWidth="1"
        fill="none"
        fillRule="evenodd"
      >
        <g
          id="-copy"
          transform="translate(0, 0.875)"
          fillRule="nonzero"
        >
          <path
            d="M82.1875,197.25 C73.0955094,197.25 65.75,189.904498 65.75,180.8125 L65.75,32.875 C65.75,23.7830015 73.0955094,16.4375 82.1875,16.4375 L156.15625,16.4375 L156.15625,57.53125 C156.15625,66.6232485 163.501752,73.96875 172.59375,73.96875 L213.6875,73.96875 C213.6875,74.1228453 213.6875,74.2255859 213.6875,74.3796812 L213.6875,180.8125 C213.6875,189.904498 206.341998,197.25 197.25,197.25 L82.1875,197.25 Z M172.59375,29.5361328 L200.332031,57.53125 L172.59375,57.53125 L172.59375,29.5361328 Z M82.1875,0 C64.0548812,0 49.3125,14.7423891 49.3125,32.875 L49.3125,180.8125 C49.3125,198.945111 64.0548812,213.6875 82.1875,213.6875 L197.25,213.6875 C215.382611,213.6875 230.125,198.945111 230.125,180.8125 L230.125,74.3796812 C230.125,67.8560578 227.556641,61.640625 222.984964,57.0175781 L173.672464,7.2941469 C169.049417,2.6197297 162.731244,0 156.15625,0 L82.1875,0 Z M16.4375,57.53125 C16.4375,53.0109438 12.7390641,49.3125 8.21875,49.3125 C3.69843593,49.3125 0,53.0109438 0,57.53125 L0,197.25 C0,233.566608 29.4334,263 65.75,263 L172.59375,263 C177.114056,263 180.8125,259.301556 180.8125,254.78125 C180.8125,250.260944 177.114056,246.5625 172.59375,246.5625 L65.75,246.5625 C38.5253906,246.5625 16.4375,224.474609 16.4375,197.25 L16.4375,57.53125 Z"
            id="Shape"
          />
        </g>
      </g>
    </svg>
  ),
  t7: (
    <svg
      className="svg-inline--fa"
      viewBox="0 0 250 250"
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>Combined Shape</title>
      <g
        id="Page-1"
        stroke="none"
        strokeWidth="1"
        fill="none"
        fillRule="evenodd"
      >
        <g
          id="t"
          transform="translate(-106, -55)"
          fillRule="nonzero"
        >
          <path
            d="M138.875,71.75 C129.783009,71.75 122.4375,79.0955015 122.4375,88.1875 L122.4375,252.5625 C122.4375,261.654498 129.783009,269 138.875,269 L303.25,269 C312.341998,269 319.6875,261.654498 319.6875,252.5625 L319.6875,88.1875 C319.6875,79.0955015 312.341998,71.75 303.25,71.75 L138.875,71.75 Z M106,88.1875 C106,70.0548891 120.742381,55.3125 138.875,55.3125 L303.25,55.3125 C321.382611,55.3125 336.125,70.0548891 336.125,88.1875 L336.125,252.5625 C336.125,270.695111 321.382611,285.4375 303.25,285.4375 L138.875,285.4375 C120.742381,285.4375 106,270.695111 106,252.5625 L106,88.1875 Z M137.90625,115.625 C134.633202,115.625 132,118.258206 132,121.53125 C132,124.804294 134.633202,127.4375 137.90625,127.4375 L173.34375,127.4375 L173.34375,219.96875 C173.34375,223.241794 175.976952,225.875 179.25,225.875 C182.523048,225.875 185.15625,223.241794 185.15625,219.96875 L185.15625,127.4375 L220.59375,127.4375 C223.866794,127.4375 226.5,124.804294 226.5,121.53125 C226.5,118.258206 223.866794,115.625 220.59375,115.625 L179.25,115.625 L137.90625,115.625 Z M230.763154,121.53125 C230.763154,118.258206 233.39636,115.625 236.669408,115.625 L303.606908,115.625 C305.723316,115.625 307.692066,116.781644 308.750266,118.627347 C309.808466,120.47305 309.759252,122.761719 308.676441,124.582811 L249.613941,223.020311 C247.940502,225.825778 244.298314,226.711717 241.517454,225.038283 C238.736594,223.364848 237.801437,219.722656 239.499482,216.9418 L293.172531,127.4375 L236.669404,127.4375 C233.396357,127.4375 230.763154,124.804294 230.763154,121.53125 L230.763154,121.53125 Z"
            id="Combined-Shape"
          />
        </g>
      </g>
    </svg>
  ),
  website: (
    <svg
      className="svg-inline--fa"
      viewBox="0 0 250 250"
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>globe</title>
      <g
        id="Page-1"
        stroke="none"
        strokeWidth="1"
        fill="none"
        fillRule="evenodd"
      >
        <g
          id="globe"
          transform="translate(-0, 0.875)"
          fillRule="nonzero"
        >
          <path
            d="M131.500006,246.5625 C140.078332,246.5625 152.252346,239.165628 163.296292,217.129108 C168.38164,206.958411 172.645126,194.681641 175.675787,180.8125 L87.3242246,180.8125 C90.3548856,194.681641 94.6183637,206.958395 99.70372,217.129108 C110.747665,239.165628 122.921687,246.5625 131.500006,246.5625 Z M84.3962965,164.375 L178.603723,164.375 C180.041998,153.998822 180.812506,142.954877 180.812506,131.5 C180.812506,120.045123 180.041998,109.00117 178.603723,98.625 L84.3962965,98.625 C82.9580137,109.00117 82.1875059,120.045116 82.1875059,131.5 C82.1875059,142.954877 82.9580137,153.998822 84.3962965,164.375 Z M87.3242246,82.1875 L175.675787,82.1875 C172.645126,68.3183594 168.38164,56.0416047 163.296292,45.8708922 C152.252346,23.8343719 140.078332,16.4375 131.500006,16.4375 C122.921679,16.4375 110.747665,23.8343719 99.70372,45.8708922 C94.6183637,56.0416047 90.3548856,68.3183594 87.3242246,82.1875 Z M195.195318,98.625 C196.530868,109.155273 197.250006,120.147848 197.250006,131.5 C197.250006,142.852152 196.530868,153.844727 195.195318,164.375 L241.836718,164.375 C244.91875,153.947467 246.613861,142.903522 246.613861,131.5 C246.613861,120.096478 244.970104,109.052541 241.836718,98.625 L195.195318,98.625 Z M235.518561,82.1875 C222.214462,54.1923828 197.969143,32.4126984 168.278915,22.4474672 C179.066025,36.984375 187.592981,57.7880859 192.524234,82.1875 L235.569947,82.1875 L235.518561,82.1875 Z M70.5785184,82.1875 C75.5097715,57.7367156 84.0367199,36.984375 94.8238293,22.4474672 C65.0822309,32.4126984 40.7855496,54.1923828 27.5328137,82.1875 L70.527148,82.1875 L70.5785184,82.1875 Z M21.2660184,98.625 C18.1839871,109.052541 16.4888684,120.096486 16.4888684,131.5 C16.4888684,142.903522 18.1326168,153.947467 21.2660184,164.375 L67.8046934,164.375 C66.4691434,153.844727 65.7500059,142.852152 65.7500059,131.5 C65.7500059,120.147848 66.4691434,109.155273 67.8046934,98.625 L21.2146559,98.625 L21.2660184,98.625 Z M168.227545,240.552533 C197.917773,230.535931 222.163092,208.807617 235.46719,180.8125 L192.472864,180.8125 C187.541611,205.263284 179.014654,226.015625 168.227545,240.552533 Z M94.7724668,240.552533 C83.9853574,226.015625 75.5097715,205.211914 70.5271559,180.8125 L27.5328137,180.8125 C40.8369199,208.807617 65.0822309,230.587302 94.7724668,240.552533 Z M131.5,263 C84.5195806,263 41.1078721,237.936236 17.6176595,197.25 C-5.87255316,156.563764 -5.87255316,106.436244 17.6176595,65.75 C41.1078721,25.0637639 84.5195806,0 131.5,0 C178.480431,0 221.892132,25.0637639 245.382352,65.75 C268.872557,106.436244 268.872557,156.563764 245.382352,197.25 C221.892132,237.936236 178.480431,263 131.5,263 Z"
            id="Shape"
          />
        </g>
      </g>
    </svg>
  ),
};

function AnnualReportRegularSlide({
  slide,
  lang,
  fadeableClass,
  revealableClass,
  dimUI,
}) {
  const isLarge = useMediaQuery('(min-width: 992px)');

  return (
    <AnimatePresence mode="sync">
      <motion.div
        className="annual-report-slide"
        key={slide.id}
        variants={isLarge ? variants : {}}
        initial={isLarge ? 'initial' : false}
        animate={isLarge ? 'animate' : false}
      >
        <div
          className={`background-row ${slide.slide_type.replace(
            '_',
            '-',
          )}-background d-none d-lg-block`}
        >
          <div
            className={`background-image ${slide.slide_type.replace(
              '_',
              '-',
            )}-background-img ${
              slide.slide_type === 'chairs_message'
              || slide.slide_type === 'presidents_message'
                ? revealableClass
                : ''
            }`}
            style={{
              backgroundImage: `url(${slide.background_image}),url(${slide.background_image_thumbnail})`,
            }}
          />
          <div>
            <div
              className={`${revealableClass} hover-reveal-gradient-${slide.background_gradient_position}`}
            >
              {slide.background_quote && (
                <div
                  className={`quote quote-${slide.background_quote_position}`}
                >
                  <h3
                    className={`hover-reveal-quote ${
                      dimUI ? 'is-revealed' : ''
                    }`}
                    dangerouslySetInnerHTML={{
                      __html:
                        lang === 'fr'
                          ? slide.background_quote_fr
                          : slide.background_quote,
                    }}
                  />
                  <div
                    className={`hover-reveal-quote-line ${
                      dimUI ? 'is-revealed' : ''
                    }`}
                  />
                </div>
              )}
            </div>
          </div>
          {slide.background_video && (
            <video
              className="background-video"
              autoPlay
              loop
              muted
              playsInline
              src={slide.background_video}
            />
          )}
          {slide.slide_type === 'standard' && (
            <>
              <div className={`background-overlay ${fadeableClass}`} />
              <div className={`background-gradient-overlay ${fadeableClass}`} />
            </>
          )}
        </div>
        <div
          className={`ar-slide-content regular-slide ${fadeableClass} ${slide.slide_type.replace(
            '_',
            '-',
          )}`}
          key={`${slide.slug}-${lang}`}
        >
          <div className="container">
            <div className="row">
              <div className="col">
                <div className="slide-title" key={lang}>
                  <h1 aria-live="assertive">
                    {lang === 'fr' ? slide.slide_title_fr : slide.slide_title}
                  </h1>
                </div>
              </div>
            </div>
            <div className="row">
              {slide.slide_content.columns?.map((column, index) => (
                <div className="col-12 col-lg-6" key={index}>
                  {column.en && (
                    <div
                      className="paragraphs"
                      key={lang}
                      dangerouslySetInnerHTML={{
                        __html: lang === 'fr' ? column.fr : column.en,
                      }}
                    />
                  )}
                  {column.content && (
                    <div className="content-links" key={`content-${lang}`}>
                      <div>
                        {column.content.map((contentBlock, idx) => (
                          <a
                            key={`content-${idx}-${lang}`}
                            className="content-link d-none d-lg-block"
                            href={contentBlock.link}
                            aria-label={
                              contentBlock.label || 'Related content link'
                            }
                          >
                            <div className="float-left content-link-icon">
                              {contentIcons[contentBlock.type] ? (
                                <FontAwesomeIcon
                                  icon={contentIcons[contentBlock.type]}
                                />
                              ) : (
                                customIcons[contentBlock.type] && (
                                  <>{customIcons[contentBlock.type]}</>
                                )
                              )}
                            </div>
                            <div className="content-copy">
                              <h4>
                                {contentBlock.type_override
                                  || contentBlock.type}
                              </h4>
                              <p>
                                <span className="underline">
                                  {lang === 'fr'
                                    ? contentBlock.title_fr
                                    : contentBlock.title_en}
                                </span>
                              </p>
                            </div>
                          </a>
                        ))}
                      </div>
                      <div className="content-links-mobile d-lg-none">
                        {column.content.map((contentBlock, idx) => (
                          <a
                            key={`mobile-${idx}`}
                            className="clearfix content-link-mobile"
                            href={contentBlock.link}
                            aria-label={
                              contentBlock.label || 'Related content link'
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {lang === 'fr'
                              ? contentBlock.title_fr
                              : contentBlock.title_en}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

AnnualReportRegularSlide.propTypes = {
  slide: PropTypes.object.isRequired,
  lang: PropTypes.string.isRequired,
  fadeableClass: PropTypes.string.isRequired,
  revealableClass: PropTypes.string.isRequired,
  dimUI: PropTypes.bool.isRequired,
};

export default AnnualReportRegularSlide;
