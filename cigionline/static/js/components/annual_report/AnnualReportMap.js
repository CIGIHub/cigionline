import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import * as maplibregl from 'maplibre-gl';
maplibregl.setWorkerUrl(
  new URL('maplibre-gl/dist/maplibre-gl-worker.mjs', import.meta.url).toString(),
);
import 'maplibre-gl/dist/maplibre-gl.css';
import '../../../css/components/annual_reports/AnnualReportMap.scss';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeadphones as faHeadphonesSolid } from '@fortawesome/free-solid-svg-icons';
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
  faFileArrowUp,
  faFilePen,
} from '@fortawesome/pro-light-svg-icons';

const themeClasses = {
  'AI and Transformative Technology': 'theme-ai',
  'Data, Economy, Society': 'theme-data',
  'Digitalization, Security and Democracy': 'theme-security',
  'Global Cooperation and Governance': 'theme-cooperation',
};

const countryAliases = {
  usa: 'United States of America',
  us: 'United States of America',
  'united states': 'United States of America',
  uk: 'United Kingdom',
  england: 'United Kingdom',
  scotland: 'United Kingdom',
  wales: 'United Kingdom',
  'northern ireland': 'United Kingdom',
};

const normalizeCountry = (country) => {
  const name = String(country || '').trim();
  return countryAliases[name.toLowerCase()] || name;
};

const cityHubAbbreviations = {
  toronto: 'TOR',
  ottawa: 'OTT',
};

const cityHubLocations = new Set(Object.keys(cityHubAbbreviations));

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
  submission: faFileArrowUp,
  report: faFilePen,
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
      <g id="Page-1" stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
        <g id="-copy" transform="translate(0, 0.875)" fillRule="nonzero">
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
      <g id="Page-1" stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
        <g id="t" transform="translate(-106, -55)" fillRule="nonzero">
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
      <g id="Page-1" stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
        <g id="globe" transform="translate(-0, 0.875)" fillRule="nonzero">
          <path
            d="M131.500006,246.5625 C140.078332,246.5625 152.252346,239.165628 163.296292,217.129108 C168.38164,206.958411 172.645126,194.681641 175.675787,180.8125 L87.3242246,180.8125 C90.3548856,194.681641 94.6183637,206.958395 99.70372,217.129108 C110.747665,239.165628 122.921687,246.5625 131.500006,246.5625 Z M84.3962965,164.375 L178.603723,164.375 C180.041998,153.998822 180.812506,142.954877 180.812506,131.5 C180.812506,120.045123 180.041998,109.00117 178.603723,98.625 L84.3962965,98.625 C82.9580137,109.00117 82.1875059,120.045116 82.1875059,131.5 C82.1875059,142.954877 82.9580137,153.998822 84.3962965,164.375 Z M87.3242246,82.1875 L175.675787,82.1875 C172.645126,68.3183594 168.38164,56.0416047 163.296292,45.8708922 C152.252346,23.8343719 140.078332,16.4375 131.500006,16.4375 C122.921679,16.4375 110.747665,23.8343719 99.70372,45.8708922 C94.6183637,56.0416047 90.3548856,68.3183594 87.3242246,82.1875 Z M195.195318,98.625 C196.530868,109.155273 197.250006,120.147848 197.250006,131.5 C197.250006,142.852152 196.530868,153.844727 195.195318,164.375 L241.836718,164.375 C244.91875,153.947467 246.613861,142.903522 246.613861,131.5 C246.613861,120.096478 244.970104,109.052541 241.836718,98.625 L195.195318,98.625 Z M235.518561,82.1875 C222.214462,54.1923828 197.969143,32.4126984 168.278915,22.4474672 C179.066025,36.984375 187.592981,57.7880859 192.524234,82.1875 L235.569947,82.1875 L235.518561,82.1875 Z M70.5785184,82.1875 C75.5097715,57.7367156 84.0367199,36.984375 94.8238293,22.4474672 C65.0822309,32.4126984 40.7855496,54.1923828 27.5328137,82.1875 L70.527148,82.1875 L70.5785184,82.1875 Z M21.2660184,98.625 C18.1839871,109.052541 16.4888684,120.096486 16.4888684,131.5 C16.4888684,142.903522 18.1326168,153.947467 21.2660184,164.375 L67.8046934,164.375 C66.4691434,153.844727 65.7500059,142.852152 65.7500059,131.5 C65.7500059,120.147848 66.4691434,109.155273 67.8046934,98.625 L21.2146559,98.625 L21.2660184,98.625 Z M168.227545,240.552533 C197.917773,230.535931 222.163092,208.807617 235.46719,180.8125 L192.472864,180.8125 C187.541611,205.263284 179.014654,226.015625 168.227545,240.552533 Z M94.7724668,240.552533 C83.9853574,226.015625 75.5097715,205.211914 70.5271559,180.8125 L27.5328137,180.8125 C40.8369199,208.807617 65.0822309,230.587302 94.7724668,240.552533 Z M131.5,263 C84.5195806,263 41.1078721,237.936236 17.6176595,197.25 C-5.87255316,156.563764 -5.87255316,106.436244 17.6176595,65.75 C41.1078721,25.0637639 84.5195806,0 131.5,0 C178.480431,0 221.892132,25.0637639 245.382352,65.75 C268.872557,106.436244 268.872557,156.563764 245.382352,197.25 C221.892132,237.936236 178.480431,263 131.5,263 Z"
            id="Shape"
          />
        </g>
      </g>
    </svg>
  ),
};

const storyMatches = (story, query, selectedTheme) => {
  const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);

  const matchesSearch =
    !words.length ||
    [story.title, story.location, story.country, story.research_theme].some((value) => {
      const text = String(value || '').toLowerCase();
      return words.every((word) => text.includes(word));
    });

  return matchesSearch && (!selectedTheme || story.research_theme === selectedTheme);
};

function AnnualReportMap({ slide }) {
  const mapContainerRef = useRef(null);
  const cardRef = useRef(null);
  const descriptionRef = useRef(null);
  const [hasMoreDescription, setHasMoreDescription] = useState(false);
  const oceanMarkersRef = useRef([]);
  const [activeStory, setActiveStory] = useState(null);
  const [hasInteractedWithMap, setHasInteractedWithMap] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [themeDropdownOpen, setThemeDropdownOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isLargeScreen, setIsLargeScreen] = useState(window.innerWidth >= 992);

  const themeDropdownRef = useRef(null);
  const highlightMarkersRef = useRef([]);
  const cityHubMarkersRef = useRef([]);

  const { stories, countries } = useMemo(
    () => ({
      stories: slide.slide_content?.map_stories || [],
      countries: slide.slide_content?.countries || {},
    }),
    [slide.slide_content],
  );

  const researchThemes = [
    ...new Set(stories.map((story) => story.research_theme).filter(Boolean)),
  ].sort();

  useLayoutEffect(() => {
    if (activeStory && cardRef.current) {
      cardRef.current.scrollTop = 0;
    }
  }, [activeStory]);

  useEffect(() => {
    cityHubMarkersRef.current.forEach(({ element, group }) => {
      const hasActiveStory = activeStory && group.includes(activeStory);

      if (!hasActiveStory) {
        element.classList.remove('is-pinned');

        if (!element.matches(':hover')) {
          element.classList.remove('is-expanded');
        }
      }
    });

    const pinnedHub = cityHubMarkersRef.current.find(({ element }) =>
      element.classList.contains('is-pinned'),
    );

    cityHubMarkersRef.current.forEach(({ element }) => {
      element.classList.toggle('is-blocked', Boolean(pinnedHub && pinnedHub.element !== element));
    });

    const anyHubExpanded = cityHubMarkersRef.current.some(({ element }) =>
      element.classList.contains('is-expanded'),
    );

    if (!anyHubExpanded) {
      mapContainerRef.current
        ?.querySelectorAll('.map-story-node.is-dimmed')
        .forEach((element) => element.classList.remove('is-dimmed'));
    }
  }, [activeStory]);

  useLayoutEffect(() => {
    const description = descriptionRef.current;

    if (!activeStory || !description) {
      setHasMoreDescription(false);
      return undefined;
    }

    const updateScrollState = () => {
      const remaining = description.scrollHeight - description.clientHeight - description.scrollTop;

      setHasMoreDescription(remaining > 2);
    };

    description.scrollTop = 0;
    updateScrollState();

    const observer = new ResizeObserver(updateScrollState);
    observer.observe(description);

    description.addEventListener('scroll', updateScrollState);

    return () => {
      observer.disconnect();
      description.removeEventListener('scroll', updateScrollState);
    };
  }, [activeStory]);

  useEffect(() => {
    if (!activeStory) return undefined;

    const handleOutsideClick = (event) => {
      if (event.target.closest('.map-story-panel') || event.target.closest('.map-story-node')) {
        return;
      }

      setActiveStory(null);
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setActiveStory(null);
      }
    };

    document.addEventListener('click', handleOutsideClick);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('click', handleOutsideClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [activeStory]);

  useEffect(() => {
    const handleOutsideHubClick = (event) => {
      if (event.target.closest('.map-city-hub')) return;

      cityHubMarkersRef.current.forEach(({ element }) => {
        element.classList.remove('is-expanded');
      });

      highlightMarkersRef.current.forEach(({ element }) => {
        element.classList.remove('is-dimmed');
      });
    };

    document.addEventListener('click', handleOutsideHubClick);

    return () => {
      document.removeEventListener('click', handleOutsideHubClick);
    };
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current) return undefined;

    let highlightAnimation = null;

    const mapWidth = mapContainerRef.current.clientWidth;
    const initialZoom = Math.max(1, Math.min(5, Math.log2(mapWidth / (512 * 0.95))));

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: {
              'background-color': '#080e17',
            },
          },
        ],
      },
      center: [-80, 20],
      zoom: initialZoom,
      minZoom: initialZoom,
      maxZoom: 5,
      attributionControl: false,
      trackResize: true,
    });

    map.addControl(
      new maplibregl.NavigationControl({
        showCompass: false,
        showZoom: true,
      }),
      'top-right',
    );

    const hideMapTitle = () => {
      setHasInteractedWithMap(true);
    };

    const hideMapTitleOnGesture = (event) => {
      if (event.originalEvent) {
        hideMapTitle();
      }
    };

    map.on('zoomstart', hideMapTitleOnGesture);
    map.on('dragstart', hideMapTitleOnGesture);
    map.on('click', hideMapTitle);

    map.on('load', () => {
      map.addSource('countries', {
        type: 'geojson',
        data: '/static/assets/ne_110m_admin_0_countries.geojson',
      });

      map.addLayer({
        id: 'countries-fill',
        type: 'fill',
        source: 'countries',
        paint: {
          'fill-color': '#3D0311',
          'fill-opacity': 1,
        },
      });

      map.addLayer({
        id: 'countries-border',
        type: 'line',
        source: 'countries',
        paint: {
          'line-color': '#E6023B',
          'line-width': 0.75,
        },
      });

      let currentOpacity = 1;
      let highlightedCountry = null;

      const setHighlightedCountry = (country) => {
        if (highlightAnimation !== null) {
          cancelAnimationFrame(highlightAnimation);
        }

        if (country) {
          highlightedCountry = country;
        }

        const startOpacity = currentOpacity;
        const targetOpacity = country ? 0.2 : 1;
        const startTime = window.performance.now();
        const duration = 400;

        const animate = (now) => {
          const progress = Math.min((now - startTime) / duration, 1);
          const eased = progress * progress * (3 - 2 * progress);

          currentOpacity = startOpacity + (targetOpacity - startOpacity) * eased;

          const opacity = highlightedCountry
            ? ['case', ['==', ['get', 'ADMIN'], highlightedCountry], 1, currentOpacity]
            : currentOpacity;

          map.setPaintProperty('countries-fill', 'fill-opacity', opacity);
          map.setPaintProperty('countries-border', 'line-opacity', opacity);

          if (progress < 1) {
            highlightAnimation = requestAnimationFrame(animate);
          } else {
            highlightAnimation = null;

            if (!country) {
              highlightedCountry = null;
              map.setPaintProperty('countries-fill', 'fill-opacity', 1);
              map.setPaintProperty('countries-border', 'line-opacity', 1);
            }
          }
        };

        highlightAnimation = requestAnimationFrame(animate);
      };

      const oceans = [
        { name: 'Pacific Ocean', coordinates: [-145, 0] },
        { name: 'Atlantic Ocean', coordinates: [-35, 30] },
        { name: 'Indian Ocean', coordinates: [80, -25] },
        { name: 'Southern Ocean', coordinates: [0, -62] },
        { name: 'Arctic Ocean', coordinates: [0, 82] },
      ];

      oceans.forEach(({ name, coordinates }) => {
        const element = document.createElement('div');
        element.className = 'map-ocean-label';
        element.textContent = name;

        const marker = new maplibregl.Marker({
          element,
          anchor: 'center',
          subpixelPositioning: true,
        })
          .setLngLat(coordinates)
          .addTo(map);

        oceanMarkersRef.current.push(marker);
      });

      const locationGroups = {};
      const cityHubGroups = {};

      stories.forEach((story) => {
        const location = story.location.trim();
        const city = location.split(',')[0].trim().toLowerCase();

        if (cityHubLocations.has(city)) {
          if (!cityHubGroups[city]) {
            cityHubGroups[city] = [];
          }

          cityHubGroups[city].push(story);
        }

        if (!locationGroups[location]) {
          locationGroups[location] = [];
        }

        locationGroups[location].push(story);
      });

      const markers = [];
      highlightMarkersRef.current = markers;

      Object.entries(locationGroups).forEach(([location, group]) => {
        const city = location.split(',')[0].trim().toLowerCase();

        if (cityHubLocations.has(city)) return;

        const coordinates = group[0].coordinates || countries[group[0].country];

        if (!coordinates) return;

        group.forEach((story, index) => {
          const element = document.createElement('button');
          element.type = 'button';
          element.setAttribute('aria-label', story.title);
          element.className = ['map-story-node', themeClasses[story.research_theme] || '']
            .filter(Boolean)
            .join(' ');

          element.innerHTML = '<div class="map-story-node-circle"></div>';

          const marker = new maplibregl.Marker({
            element,
            anchor: 'center',
            subpixelPositioning: true,
          })
            .setLngLat([coordinates.longitude, coordinates.latitude])
            .addTo(map);

          const tooltipContent = document.createElement('div');
          tooltipContent.className = 'map-story-title-tooltip';
          tooltipContent.textContent = story.title;

          const tooltip = new maplibregl.Popup({
            closeButton: false,
            closeOnClick: false,
            anchor: 'bottom',
            offset: 18,
            className: 'map-story-tooltip',
          }).setDOMContent(tooltipContent);

          element.addEventListener('mouseenter', () => {
            tooltip.setLngLat(marker.getLngLat()).addTo(map);
            setHighlightedCountry(normalizeCountry(story.country));
          });

          element.addEventListener('mouseleave', () => {
            tooltip.remove();
            setHighlightedCountry(null);
          });

          element.addEventListener('click', (event) => {
            event.stopPropagation();
            tooltip.remove();
            setHasInteractedWithMap(true);

            cityHubMarkersRef.current.forEach(({ element: hubElement }) => {
              hubElement.classList.remove('is-expanded');
            });

            markers.forEach(({ element: storyElement }) => {
              storyElement.classList.remove('is-dimmed');
            });

            setActiveStory(story);

            map.easeTo({
              center: marker.getLngLat().toArray(),
              duration: 800,
            });
          });

          markers.push({ marker, coordinates, index, story, element, tooltip });
        });
      });

      Object.entries(cityHubGroups).forEach(([city, group]) => {
        const coordinates = group[0].coordinates || countries[group[0].country];

        if (!coordinates) return;

        const hubSize = Math.min(65, 28 + Math.sqrt(group.length) * 5) / 1.5;

        const element = document.createElement('div');
        element.className = 'map-city-hub';
        element.style.setProperty('--hub-size', `${hubSize}px`);
        element.innerHTML = `
          <div class="map-city-hub-circle">
            <span>${cityHubAbbreviations[city]}</span>
          </div>
        `;

        element.setAttribute('aria-label', `${city}: ${group.length} stories`);

        const hubTooltip = document.createElement('div');
        hubTooltip.className = 'map-city-hub-info';

        hubTooltip.innerHTML = `
          <div class="map-city-hub-info-title">
            ${city.charAt(0).toUpperCase() + city.slice(1)}
          </div>
          <div class="map-city-hub-info-count">
            ${group.length} ${group.length === 1 ? 'story' : 'stories'}
          </div>
        `;

        element.querySelector('.map-city-hub-circle').appendChild(hubTooltip);

        const radius = Math.max(70, group.length * 12);
        const cityHubNodes = [];

        group.forEach((story, index) => {
          const angleStep = group.length <= 7 ? Math.PI / 6 : Math.PI / (group.length - 1);

          const angle = Math.PI / 2 + index * angleStep;

          const node = document.createElement('button');
          node.type = 'button';

          node.className = [
            'map-city-hub-story',
            'map-story-node',
            themeClasses[story.research_theme] || '',
          ]
            .filter(Boolean)
            .join(' ');

          node.style.setProperty('--node-x', `${Math.cos(angle) * radius}px`);
          node.style.setProperty('--node-y', `${Math.sin(angle) * radius}px`);

          node.innerHTML = '<span class="map-story-node-circle"></span>';
          node.setAttribute('aria-label', story.title);

          const tooltip = document.createElement('span');
          tooltip.className = 'map-city-hub-tooltip';
          tooltip.textContent = story.title;
          tooltip.setAttribute('aria-hidden', 'true');

          node.appendChild(tooltip);

          node.addEventListener('click', (event) => {
            event.stopPropagation();
            setHasInteractedWithMap(true);
            element.classList.add('is-pinned');
            setActiveStory(story);

            map.easeTo({
              center: hub.getLngLat().toArray(),
              duration: 800,
            });
          });

          element.appendChild(node);
          cityHubNodes.push({ story, node });
        });

        let collapseTimer;

        element.addEventListener('mouseenter', () => {
          clearTimeout(collapseTimer);

          const anotherHubPinned = cityHubMarkersRef.current.some(
            ({ element: otherElement }) =>
              otherElement !== element && otherElement.classList.contains('is-pinned'),
          );

          element.classList.toggle('is-blocked', anotherHubPinned);

          if (anotherHubPinned) return;

          cityHubMarkersRef.current.forEach(({ element: otherElement }) => {
            if (otherElement !== element) {
              otherElement.classList.remove('is-expanded');
            }
          });

          element.classList.add('is-expanded');

          markers.forEach(({ element: storyElement }) => {
            storyElement.classList.add('is-dimmed');
          });
        });

        element.addEventListener('mouseleave', () => {
          clearTimeout(collapseTimer);

          collapseTimer = setTimeout(
            () => {
              if (element.matches(':hover') || element.classList.contains('is-pinned')) return;

              element.classList.remove('is-expanded');

              const anyHubExpanded = cityHubMarkersRef.current.some(({ element: hubElement }) =>
                hubElement.classList.contains('is-expanded'),
              );

              if (!anyHubExpanded) {
                markers.forEach(({ element: storyElement }) => {
                  storyElement.classList.remove('is-dimmed');
                });
              }
            },
            Math.min(
              1400,
              Math.max(
                650,
                500 +
                  (cityHubNodes.filter(({ node }) => node.style.display !== 'none').length - 7) *
                    112.5,
              ),
            ),
          );
        });

        element.addEventListener('click', (event) => {
          if (!window.matchMedia('(hover: none)').matches) return;

          if (event.target.closest('.map-city-hub-story')) return;

          element.classList.toggle('is-expanded');
        });

        const hub = new maplibregl.Marker({
          element,
          anchor: 'center',
          subpixelPositioning: true,
        })
          .setLngLat([coordinates.longitude, coordinates.latitude])
          .addTo(map);

        oceanMarkersRef.current.push(hub);
        cityHubMarkersRef.current.push({
          hub,
          element,
          group,
          nodes: cityHubNodes,
        });
      });

      const isValidLandPosition = (center, candidate, country) => {
        const isInsideCountry = (point) =>
          map
            .queryRenderedFeatures(point, { layers: ['countries-fill'] })
            .some((feature) => feature.properties.ADMIN === normalizeCountry(country));

        if (!isInsideCountry(candidate)) return false;

        const distance = Math.hypot(candidate[0] - center.x, candidate[1] - center.y);

        const steps = Math.ceil(distance / 4);

        for (let step = 1; step < steps; step += 1) {
          const progress = step / steps;

          const point = [
            center.x + (candidate[0] - center.x) * progress,
            center.y + (candidate[1] - center.y) * progress,
          ];

          if (!isInsideCountry(point)) return false;
        }

        return true;
      };

      const updateStoryPositions = () => {
        const placedPositions = [];
        const minimumDistance = 12;

        const hubs = cityHubMarkersRef.current
          .map(({ hub, element, group }) => {
            const coordinates = group[0].coordinates || countries[group[0].country];

            if (!coordinates) return null;

            const center = map.project([coordinates.longitude, coordinates.latitude]);

            return {
              hub,
              center,
              radius: parseFloat(element.style.getPropertyValue('--hub-size')) / 2,
              x: center.x,
              y: center.y,
            };
          })
          .filter(Boolean);

        // Separate hubs only when their circles are too close.
        for (let i = 0; i < hubs.length; i += 1) {
          for (let j = i + 1; j < hubs.length; j += 1) {
            const a = hubs[i];
            const b = hubs[j];

            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const distance = Math.hypot(dx, dy);
            const requiredDistance = a.radius + b.radius;

            if (distance >= requiredDistance) continue;

            const angle = distance > 0 ? Math.atan2(dy, dx) : 0;

            const displacement = (requiredDistance - distance) / 2;

            a.x -= Math.cos(angle) * displacement;
            a.y -= Math.sin(angle) * displacement;

            b.x += Math.cos(angle) * displacement;
            b.y += Math.sin(angle) * displacement;
          }
        }

        hubs.forEach(({ hub, x, y }) => {
          hub.setLngLat(map.unproject([x, y]));
        });

        const hubObstacles = cityHubMarkersRef.current.map(({ hub, element }) => ({
          center: map.project(hub.getLngLat()),
          radius: parseFloat(element.style.getPropertyValue('--hub-size')) / 2,
        }));

        markers.forEach(({ marker, coordinates, index, story }, markerIndex) => {
          const center = map.project([coordinates.longitude, coordinates.latitude]);

          const nearestOtherLocation = Math.min(
            ...markers
              .filter(
                ({ story: otherStory }) =>
                  otherStory.location !== story.location &&
                  !cityHubLocations.has(otherStory.location.split(',')[0].trim().toLowerCase()),
              )
              .map(({ coordinates: otherCoordinates }) => {
                const otherCenter = map.project([
                  otherCoordinates.longitude,
                  otherCoordinates.latitude,
                ]);

                return Math.hypot(center.x - otherCenter.x, center.y - otherCenter.y);
              }),
          );

          const maxDisplacement = Math.min(25, nearestOtherLocation * 0.4);
          const searchRadius = Math.max(12, maxDisplacement);

          const futurePositions = markers
            .slice(markerIndex + 1)
            .map(({ coordinates: otherCoordinates }) => {
              const point = map.project([otherCoordinates.longitude, otherCoordinates.latitude]);

              return [point.x, point.y];
            });

          let bestCandidate = [center.x, center.y];
          let bestScore = Infinity;

          // Search outward in rings, checking multiple directions at each distance.
          for (let radius = 0; radius <= searchRadius; radius += 4) {
            const angleCount = radius === 0 ? 1 : 24;

            for (let step = 0; step < angleCount; step += 1) {
              const angle = (step / angleCount) * Math.PI * 2 + index * 0.25;

              const candidateX = center.x + radius * Math.cos(angle);
              const candidateY = center.y + radius * Math.sin(angle);

              if (!isValidLandPosition(center, [candidateX, candidateY], story.country)) continue;

              // Priority 1: avoid fixed hubs.
              const hubOverlap = hubObstacles.reduce(
                (maximum, { center: hubCenter, radius: hubRadius }) => {
                  const distance = Math.hypot(candidateX - hubCenter.x, candidateY - hubCenter.y);

                  return Math.max(maximum, hubRadius + 10 - distance);
                },
                0,
              );

              // Priority 2: avoid already-positioned story nodes.
              const placedOverlap = placedPositions.reduce((total, [px, py]) => {
                const distance = Math.hypot(candidateX - px, candidateY - py);

                return total + Math.max(0, minimumDistance - distance);
              }, 0);

              // Account for story nodes that have not yet been positioned.
              const futureOverlap = futurePositions.reduce((total, [px, py]) => {
                const distance = Math.hypot(candidateX - px, candidateY - py);

                return total + Math.max(0, minimumDistance - distance);
              }, 0);

              // Hub overlap carries the highest penalty.
              // Story overlap is softer; displacement is the final consideration.
              const score =
                Math.max(0, hubOverlap) * 15 + placedOverlap * 6 + futureOverlap * 2 + radius * 0.5;

              if (score < bestScore) {
                bestScore = score;
                bestCandidate = [candidateX, candidateY];
              }
            }
          }

          placedPositions.push(bestCandidate);
          marker.setLngLat(map.unproject(bestCandidate));
        });

        // Refine placements using the actual positions of all story nodes.
        // Multiple passes allow earlier nodes to adjust around later ones.
        for (let pass = 0; pass < 3; pass += 1) {
          markers.forEach(({ marker, coordinates, story }) => {
            const center = map.project([coordinates.longitude, coordinates.latitude]);

            const current = map.project(marker.getLngLat());

            const otherPositions = markers
              .filter(({ marker: otherMarker }) => otherMarker !== marker)
              .map(({ marker: otherMarker, story: otherStory }) => ({
                position: map.project(otherMarker.getLngLat()),
                sameLocation: otherStory.location === story.location,
              }));

            const nearestOtherLocation = Math.min(
              ...markers
                .filter(({ story: otherStory }) => otherStory.location !== story.location)
                .map(({ coordinates: otherCoordinates }) => {
                  const otherCenter = map.project([
                    otherCoordinates.longitude,
                    otherCoordinates.latitude,
                  ]);

                  return Math.hypot(center.x - otherCenter.x, center.y - otherCenter.y);
                }),
            );

            const maxDisplacement = Math.min(25, nearestOtherLocation * 0.4);
            const searchRadius = Math.max(12, maxDisplacement);

            let bestCandidate = [current.x, current.y];
            let bestScore = Infinity;

            for (let radius = 0; radius <= searchRadius; radius += 3) {
              const angleCount = radius === 0 ? 1 : 24;

              for (let step = 0; step < angleCount; step += 1) {
                const angle = (step / angleCount) * Math.PI * 2;
                const candidate = [
                  center.x + radius * Math.cos(angle),
                  center.y + radius * Math.sin(angle),
                ];

                if (
                  !story.location.toLowerCase().includes('waterloo') &&
                  !isValidLandPosition(center, candidate, story.country)
                )
                  continue;

                const hubOverlap = hubObstacles.reduce(
                  (maximum, { center: hubCenter, radius: hubRadius }) => {
                    const distance = Math.hypot(
                      candidate[0] - hubCenter.x,
                      candidate[1] - hubCenter.y,
                    );

                    return Math.max(maximum, hubRadius + 10 - distance);
                  },
                  0,
                );

                const nodeOverlap = otherPositions.reduce((total, { position, sameLocation }) => {
                  const distance = Math.hypot(candidate[0] - position.x, candidate[1] - position.y);

                  const overlap = Math.max(0, minimumDistance - distance);

                  return total + overlap * (sameLocation ? 0.2 : 1);
                }, 0);

                const score =
                  Math.max(0, hubOverlap) *
                    (story.location.toLowerCase().includes('waterloo') ? 8 : 15) +
                  nodeOverlap * 6 +
                  radius * 0.5;

                if (score < bestScore) {
                  bestScore = score;
                  bestCandidate = candidate;
                }
              }
            }

            marker.setLngLat(map.unproject(bestCandidate));
          });
        }
      };

      map.on('zoom', () => {
        const zoomDifference = Math.max(0, map.getZoom() - initialZoom);
        const scale = Math.min(1.8, 1 + zoomDifference * 0.2);

        markers.forEach(({ element }) => {
          element.style.setProperty('--story-zoom-scale', scale);
        });
      });

      map.once('idle', () => {
        updateStoryPositions();

        requestAnimationFrame(() => {
          mapContainerRef.current
            ?.closest('.annual-report-map')
            ?.classList.remove('map-initializing');
        });
      });
    });

    return () => {
      if (highlightAnimation !== null) {
        cancelAnimationFrame(highlightAnimation);
        highlightAnimation = null;
      }

      highlightMarkersRef.current.forEach(({ marker, tooltip }) => {
        tooltip.remove();
        marker.remove();
      });

      highlightMarkersRef.current = [];

      oceanMarkersRef.current.forEach((marker) => {
        marker.remove();
      });

      oceanMarkersRef.current = [];

      map.remove();
    };
  }, [countries, stories]);

  useEffect(() => {
    highlightMarkersRef.current.forEach(({ story, element, tooltip }) => {
      const matches = storyMatches(story, searchQuery, selectedTheme);

      element.style.display = matches ? '' : 'none';

      if (!matches) {
        tooltip.remove();
      }
    });

    cityHubMarkersRef.current.forEach(({ element, nodes }) => {
      const matchingNodes = nodes.filter(({ story }) =>
        storyMatches(story, searchQuery, selectedTheme),
      );

      const matchingCount = matchingNodes.length;
      const radius = Math.max(70, matchingCount * 12);

      nodes.forEach(({ node }) => {
        node.style.display = 'none';
      });

      matchingNodes.forEach(({ node }, index) => {
        const angleStep = matchingCount <= 7 ? Math.PI / 6 : Math.PI / (matchingCount - 1);

        const angle = Math.PI / 2 + index * angleStep;

        node.style.setProperty('--node-x', `${Math.cos(angle) * radius}px`);
        node.style.setProperty('--node-y', `${Math.sin(angle) * radius}px`);

        node.style.display = '';
      });

      element.style.display = matchingCount > 0 ? '' : 'none';

      const hubSize = Math.min(65, 28 + Math.sqrt(matchingCount) * 5) / 1.5;
      element.style.setProperty('--hub-size', `${hubSize}px`);

      const tooltipCount = element.querySelector('.map-city-hub-info-count');

      if (tooltipCount) {
        tooltipCount.textContent = `${matchingCount} ${matchingCount === 1 ? 'story' : 'stories'}`;
      }
    });
  }, [searchQuery, selectedTheme]);

  useEffect(() => {
    const mobileQuery = window.matchMedia('(max-width: 768px)');
    const largeQuery = window.matchMedia('(min-width: 992px)');

    const updateMobile = (event) => setIsMobile(event.matches);
    const updateLarge = (event) => setIsLargeScreen(event.matches);

    mobileQuery.addEventListener('change', updateMobile);
    largeQuery.addEventListener('change', updateLarge);

    return () => {
      mobileQuery.removeEventListener('change', updateMobile);
      largeQuery.removeEventListener('change', updateLarge);
    };
  }, []);

  useEffect(() => {
    if (!themeDropdownOpen) return undefined;

    const handlePointerDown = (event) => {
      if (!themeDropdownRef.current?.contains(event.target)) {
        setThemeDropdownOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setThemeDropdownOpen(false);
        themeDropdownRef.current?.querySelector('.map-theme-trigger')?.focus();
      }
    };

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [themeDropdownOpen]);

  return (
    <motion.div
      className="annual-report-map map-initializing"
      initial={isLargeScreen ? { opacity: 0, y: 20 } : false}
      animate={
        isLargeScreen
          ? {
              opacity: 1,
              y: 0,
              transition: { duration: 0.5, ease: 'easeInOut' },
            }
          : false
      }
    >
      <div
        className={`annual-report-slide map-title-overlay${hasInteractedWithMap ? ' is-hidden' : ''}`}
      >
        <div className="ar-slide-content regular-slide standard">
          <div className="container">
            <div className="row">
              <div className="col">
                <div className="slide-title">
                  <h1>{slide.title}</h1>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="annual-report-map-controls">
        <div className="map-search-input">
          <input
            type="search"
            placeholder="Search stories..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            aria-label="Search stories"
          />
          <i className="fa-solid fa-magnifying-glass" aria-hidden="true" />
        </div>

        <div className="map-theme-select" ref={themeDropdownRef}>
          <button
            type="button"
            className="map-theme-trigger"
            aria-expanded={themeDropdownOpen}
            onClick={() => setThemeDropdownOpen(!themeDropdownOpen)}
          >
            <span>{selectedTheme || (isMobile ? 'All' : 'All research themes')}</span>
            <i className="fa-solid fa-chevron-down" aria-hidden="true" />
          </button>

          {themeDropdownOpen && (
            <div className="map-theme-options">
              <button
                type="button"
                aria-pressed={!selectedTheme}
                onClick={() => {
                  setSelectedTheme('');
                  setThemeDropdownOpen(false);
                }}
              >
                All research themes
              </button>

              {researchThemes.map((theme) => (
                <button
                  key={theme}
                  type="button"
                  aria-pressed={selectedTheme === theme}
                  onClick={() => {
                    setSelectedTheme(theme);
                    setThemeDropdownOpen(false);
                  }}
                >
                  {theme}
                </button>
              ))}
            </div>
          )}
        </div>

        {(searchQuery || selectedTheme) && (
          <button
            type="button"
            className="map-search-clear"
            onClick={() => {
              setSearchQuery('');
              setSelectedTheme('');
              setThemeDropdownOpen(false);
            }}
          >
            Clear
          </button>
        )}
      </div>
      <div ref={mapContainerRef} className="annual-report-map-container" />

      {activeStory && (
        <div className="map-story-panel">
          <button
            type="button"
            className="map-story-panel-close"
            onClick={() => setActiveStory(null)}
            aria-label="Close story card"
          >
            &times;
          </button>

          <div className="map-card" ref={cardRef}>
            {activeStory.research_theme && (
              <div className={`map-card-theme ${themeClasses[activeStory.research_theme] || ''}`}>
                {activeStory.research_theme}
              </div>
            )}

            <div className="map-card-title">{activeStory.title}</div>

            <div
              ref={descriptionRef}
              className={`map-card-content${hasMoreDescription ? ' has-more-content' : ''}`}
              tabIndex={0}
              role="region"
              aria-label="Story description and related content"
            >
              <div
                className="map-card-description"
                dangerouslySetInnerHTML={{
                  __html: activeStory.short_description || '',
                }}
              />

              {(activeStory.related_pages || []).length > 0 && (
                <div className="map-card-related">
                  {activeStory.related_pages.map((related, index) => (
                    <a key={`${related.url}-${index}`} href={related.url} className="content-link">
                      <div className="content-link-icon">
                        {contentIcons[related.content_type] ? (
                          <FontAwesomeIcon icon={contentIcons[related.content_type]} />
                        ) : (
                          customIcons[related.content_type] || null
                        )}
                      </div>

                      <div className="content-copy">
                        <h4>{related.type_override || related.content_type}</h4>
                        <p>
                          <span
                            className="underline"
                            dangerouslySetInnerHTML={{
                              __html: related.title || '',
                            }}
                          />
                        </p>
                      </div>
                    </a>
                  ))}
                </div>
              )}
            </div>

            <div className="map-card-meta">
              {activeStory.publishing_date && <span>{activeStory.publishing_date}</span>}
              <span>{activeStory.location}</span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}

AnnualReportMap.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default AnnualReportMap;
