import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../../../css/components/annual_reports/AnnualReportMap.scss';

const storyMatches = (story, searchQuery, selectedTheme) => {
  const words = searchQuery.trim().toLowerCase().split(/\s+/).filter(Boolean);

  const matchesSearch = !words.length || [
    story.title,
    story.location,
    story.country,
    story.research_theme,
  ].some((value) => {
    const text = String(value || '').toLowerCase();
    return words.every((word) => text.includes(word));
  });

  return matchesSearch && (
    !selectedTheme || story.research_theme === selectedTheme
  );
};

const themeClasses = {
  'AI and Transformative Technology': 'theme-ai',
  'Data, Economy, Society': 'theme-data',
  'Digitalization, Security and Democracy': 'theme-security',
  'Global Cooperation and Governance': 'theme-cooperation',
};

const getStoryPosition = (coordinates, index, map) => {
  const center = map.latLngToContainerPoint([
    coordinates.latitude,
    coordinates.longitude,
  ]);

  const angle = index * 2.39996;
  const radius = 22 * Math.sqrt(index);

  return map.containerPointToLatLng([
    center.x + radius * Math.cos(angle),
    center.y + radius * Math.sin(angle),
  ]);
};

function AnnualReportMap({ slide }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [activeStory, setActiveStory] = useState(null);
  const highlightMarkersRef = useRef([]);
  const criteriaRef = useRef({ searchQuery, selectedTheme });
  criteriaRef.current = { searchQuery, selectedTheme };

  const [isMobile, setIsMobile] = useState(
    window.innerWidth <= 768
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    const updateMobile = (event) => setIsMobile(event.matches);

    mediaQuery.addEventListener('change', updateMobile);
    return () => mediaQuery.removeEventListener('change', updateMobile);
  }, []);

  const stories = slide.slide_content?.map_stories || [];

  const researchThemes = [...new Set(
    stories
      .map((story) => story.research_theme)
      .filter(Boolean)
  )].sort();

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return undefined;

    const stories = slide.slide_content?.map_stories || [];
    const countries = slide.slide_content?.countries || {};

    const countryGroups = stories.reduce((groups, story) => {
      const country = story.country;

      if (!groups[country]) {
        groups[country] = { stories: [] };
      }

      groups[country].stories.push(story);

      return groups;
    }, {});

    const map = L.map(mapContainerRef.current, {
      minZoom: 1.5,
      maxZoom: 5,
      zoomSnap: 0,
      zoomDelta: 1,
      wheelPxPerZoomLevel: 15,
      zoomAnimation: true,
      zoomAnimationThreshold: 4,
      maxBounds: [
        [-85, -180],
        [85, 180],
      ],
      maxBoundsViscosity: 1.0,
    });

    const worldBounds = L.latLngBounds(
      [-85, -180],
      [85, 180]
    );

    const getInitialZoom = () => (
      map.getBoundsZoom(worldBounds) + Math.log2(1.5) + 0.5
    );

    const initialZoom = getInitialZoom();

    map.setView([35, 0], initialZoom);

    const updateMapSize = () => {
      map.invalidateSize();
    };

    const resizeObserver = new ResizeObserver(updateMapSize);
    resizeObserver.observe(mapContainerRef.current);

    map.attributionControl.setPrefix(false);
    map.zoomControl.setPosition('topright');
    mapRef.current = map;

    const controls = mapContainerRef.current.parentElement
      .querySelector('.annual-report-map-controls');

    if (controls) {
      L.DomEvent.disableClickPropagation(controls);
      L.DomEvent.disableScrollPropagation(controls);
    }

    requestAnimationFrame(() => {
      map.invalidateSize();
    });

    const countryLayers = {};

    const setHighlightedCountry = (country) => {
      Object.entries(countryLayers).forEach(([name, layers]) => {
        layers.forEach((layer) => {
          layer.getElement()?.classList.toggle(
            'map-country-dimmed',
            Boolean(country) && name !== country
          );

          if (country && name === country) {
            layer.bringToFront();
          }
        });
      });
    };

    fetch('/static/assets/ne_110m_admin_0_countries.geojson')
      .then((response) => {
        if (!response.ok) throw new Error('Failed to load country GeoJSON');
        return response.json();
      })
      .then((data) => {
        L.geoJSON(data, {
          style: {
            className: 'map-country',
          },
          interactive: true,

          onEachFeature: (feature, layer) => {
            const countryName = feature.properties.ADMIN;

            if (!countryLayers[countryName]) {
              countryLayers[countryName] = [];
            }

            countryLayers[countryName].push(layer);
          },
        }).addTo(map);
      })
      .catch((error) => console.error(error));

    const oceans = [
      { name: 'Pacific Ocean', coordinates: [0, -145] },
      { name: 'Atlantic Ocean', coordinates: [30, -35] },
      { name: 'Indian Ocean', coordinates: [-25, 80] },
      { name: 'Southern Ocean', coordinates: [-62, 0] },
      { name: 'Arctic Ocean', coordinates: [82, 0] },
    ];

    oceans.forEach(({ name, coordinates }) => {
      L.marker(coordinates, {
        icon: L.divIcon({
          className: 'map-ocean-label',
          html: `<span>${name}</span>`,
          iconSize: [0, 0],
        }),
        interactive: false,
        keyboard: false,
      }).addTo(map);
    });

    highlightMarkersRef.current = [];

    Object.entries(countryGroups).forEach(([country, group]) => {
      const coordinates = countries[country];

      if (!coordinates) return;

      group.stories.forEach((story, index) => {
        const position = getStoryPosition(
          coordinates,
          index,
          map
        );

        const { searchQuery: activeQuery, selectedTheme: activeTheme } = criteriaRef.current;
        const isMatch = storyMatches(story, activeQuery, activeTheme);
        const hasActiveSearch = Boolean(activeQuery.trim() || activeTheme);

        const nodeIcon = L.divIcon({
          className: [
            'map-story-node',
            themeClasses[story.research_theme] || '',
            hasActiveSearch && isMatch ? 'map-story-node-highlight' : '',
          ].filter(Boolean).join(' '),
          html: '<div class="map-story-node-circle"></div>',
          iconSize: [20, 20],
          iconAnchor: [10, 10],
        });

        const node = L.marker(position, {
          icon: nodeIcon,
          zIndexOffset: 1000,
        })
          .addTo(map)
          .bindTooltip(story.title, {
            direction: 'top',
            offset: [0, -10],
            opacity: 1,
            className: 'map-story-title-tooltip',
          });
        highlightMarkersRef.current.push({
          marker: node,
          story,
          coordinates,
          index,
        });

        node.on('mouseover', () => {
          setHighlightedCountry(story.country);
        });

        node.on('mouseout', () => {
          setHighlightedCountry(null);
        });

        node.on('click', (event) => {
          L.DomEvent.stopPropagation(event.originalEvent);

          node.closeTooltip();
          setActiveStory(story);

          map.panTo(
            [coordinates.latitude, coordinates.longitude],
            {
              animate: true,
              duration: 0.8,
            }
          );
        });
      });
    });

    const updateStoryPositions = () => {
      highlightMarkersRef.current.forEach(({ marker, coordinates, index }) => {
        marker.setLatLng(getStoryPosition(coordinates, index, map));
      });
    };

    map.on('zoomend', updateStoryPositions);

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, [slide]);

  useEffect(() => {
    const hasActiveSearch = Boolean(searchQuery.trim() || selectedTheme);

    highlightMarkersRef.current.forEach(({ marker, story }) => {
      const nodeElement = marker.getElement();

      if (nodeElement) {
        nodeElement.classList.toggle(
          'map-story-node-highlight',
          hasActiveSearch && storyMatches(story, searchQuery, selectedTheme)
        );
      }
    });
  }, [searchQuery, selectedTheme, slide]);

  useEffect(() => {
    if (!activeStory) return undefined;

    const handleOutsideClick = (event) => {
      if (
        event.target.closest('.map-story-panel') ||
        event.target.closest('.map-story-node')
      ) {
        return;
      }

      setActiveStory(null);
    };

    document.addEventListener('click', handleOutsideClick);

    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, [activeStory]);

  return (
    <div className="annual-report-map">
      <div className="annual-report-map-controls">
        <div className="map-search-input">
          <i className="fa-solid fa-magnifying-glass" aria-hidden="true" />
          <input
            type="search"
            placeholder="Search stories..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            aria-label="Search stories"
          />
        </div>

        <div className="map-theme-select">
          <select
            value={selectedTheme}
            onChange={(event) => setSelectedTheme(event.target.value)}
            aria-label="Filter by research theme"
          >
            <option value="">
              {isMobile ? 'All' : 'All research themes'}
            </option>
            {researchThemes.map((theme) => (
              <option key={theme} value={theme}>
                {theme}
              </option>
            ))}
          </select>
          <i className="fa-solid fa-chevron-down" aria-hidden="true" />
        </div>

        {(searchQuery || selectedTheme) && (
          <button
            type="button"
            className="map-search-clear"
            onClick={() => {
              setSearchQuery('');
              setSelectedTheme('');
            }}
          >
            Clear
          </button>
        )}
      </div>

      <div
        ref={mapContainerRef}
        className="annual-report-map-container"
      />

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
          <div className="map-card">
            {activeStory.research_theme && (
              <div className={`map-card-theme ${themeClasses[activeStory.research_theme] || ''}`}>
                {activeStory.research_theme}
              </div>
            )}

            <div className="map-card-title">
              {activeStory.title}
            </div>

            <div
              className="map-card-description"
              dangerouslySetInnerHTML={{
                __html: activeStory.short_description || '',
              }}
            />

            {(activeStory.related_pages || []).length > 0 && (
              <div className="map-card-related">
                {activeStory.related_pages.map((related) => {
                  const icons = {
                    ArticlePage: 'fa-pen',
                    PublicationPage: 'fa-book-open',
                    EventPage: 'fa-calendar',
                    MultimediaPage: 'fa-play',
                    PersonPage: 'fa-user',
                  };

                  const icon = icons[related.content_type] || 'fa-arrow-up-right-from-square';

                  return (
                    <a key={related.url} href={related.url}>
                      <i className={`fa-solid ${icon}`} aria-hidden="true" />
                      <span>{related.title}</span>
                    </a>
                  );
                })}
              </div>
            )}

            <div className="map-card-meta">
              <span>{activeStory.publishing_date}</span>
              <span>{activeStory.location}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

AnnualReportMap.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default AnnualReportMap;
