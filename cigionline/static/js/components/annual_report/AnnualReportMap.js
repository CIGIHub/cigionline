import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../../../css/components/annual_reports/AnnualReportMap.scss';

function AnnualReportMap({ slide }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return undefined;

    const stories = slide.slide_content?.map_stories || [];
    const countries = slide.slide_content?.countries || {};

    const countryGroups = stories.reduce((groups, story) => {
      const country = story.country;

      if (!groups[country]) {
        groups[country] = {
          country,
          stories: [],
          research_themes: [],
        };
      }

      groups[country].stories.push(story);

      if (
        story.research_theme &&
        !groups[country].research_themes.includes(story.research_theme)
      ) {
        groups[country].research_themes.push(story.research_theme);
      }

      return groups;
    }, {});

    const map = L.map(mapContainerRef.current, {
      maxZoom: 5,
      zoomSnap: 0.5,
      wheelPxPerZoomLevel: 40,
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
    map.setMinZoom(initialZoom);

    const updateMapSize = () => {
      map.invalidateSize();

      const minZoom = getInitialZoom();

      map.setMinZoom(minZoom);

      if (map.getZoom() < minZoom) {
        map.setZoom(minZoom);
      }
    };

    const resizeObserver = new ResizeObserver(updateMapSize);
    resizeObserver.observe(mapContainerRef.current);

    map.attributionControl.setPrefix(false);
    mapRef.current = map;

    requestAnimationFrame(() => {
      map.invalidateSize();
    });

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
          interactive: false,
        }).addTo(map);
      })
      .catch((error) => console.error(error));

    Object.entries(countryGroups).forEach(([country, group]) => {
      const coordinates = countries[country];

      if (!coordinates) return;

      const hubPosition = [coordinates.latitude, coordinates.longitude];

      const hubIcon = L.divIcon({
        className: 'map-country-hub',
        html: `<div class="map-country-hub-circle">${group.stories.length}</div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      });

      const hub = L.marker(hubPosition, {
        icon: hubIcon,
      })
        .addTo(map)
        .bindTooltip(`
          <div class="map-hub-card">
            <div class="map-hub-card-country">${group.country}</div>
            <ul class="map-hub-card-themes">
              ${group.research_themes.map(theme => `
                <li>${theme}</li>
              `).join('')}
            </ul>
          </div>
        `, {
          direction: 'left',
          offset: [-20, 0],
          opacity: 1,
        });

      const storyNodes = [];
      let closeTimeout;

      const collapseHub = () => {
        storyNodes.forEach((node) => {
          node.closePopup();
          map.removeLayer(node);
        });

        storyNodes.length = 0;
      };

      const expandHub = () => {
        clearTimeout(closeTimeout);

        if (storyNodes.length) return;

        const hubPoint = map.latLngToContainerPoint(hub.getLatLng());
        const count = group.stories.length;
        const radius = Math.max(90, (count - 1) * 16);
        const mapWidth = map.getSize().x;
        const expandLeft = hubPoint.x + radius + 20 > mapWidth;
        const direction = expandLeft ? -1 : 1;
        const mapHeight = map.getSize().y;

        const verticalOffset = Math.max(
          radius + 20 - hubPoint.y,
          0
        ) - Math.max(
          hubPoint.y + radius + 20 - mapHeight,
          0
        );

        group.stories.forEach((story, index) => {
          const angle = count === 1
            ? 0
            : -Math.PI / 2 + (Math.PI * index) / (count - 1);

          const x = hubPoint.x + direction * radius * Math.cos(angle);
          const y = hubPoint.y + verticalOffset + radius * Math.sin(angle);

          const position = map.containerPointToLatLng([x, y]);

          const nodeIcon = L.divIcon({
            className: 'map-story-node',
            html: '<div class="map-story-node-circle"></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10],
          });

          const relatedPages = (story.related_pages || [])
            .map((related) => `
              <a href="${related.url}">
                ${related.title}
              </a>
            `)
            .join('');

          const node = L.marker(position, {
            icon: nodeIcon,
            zIndexOffset: 1000,
          }).addTo(map);

          const popupWidth = Math.min(900, map.getSize().x - 40);
          const markerX = map.latLngToContainerPoint(node.getLatLng()).x;
          const currentMapWidth = map.getSize().x;
          const markerY = map.latLngToContainerPoint(node.getLatLng()).y;
          const mapHeight = map.getSize().y;

          // Place the popup below the node when there's insufficient room above
          const openBelow = markerY < mapHeight / 2;

          const popupOffsetX = Math.max(
            popupWidth / 2 + 20 - markerX,
            Math.min(
              0,
              currentMapWidth - popupWidth / 2 - 20 - markerX
            )
          );

          node.bindPopup(`
            <div class="map-card">
              ${story.research_theme ? `
                <div class="map-card-theme">
                  ${story.research_theme}
                </div>
              ` : ''}

              <div class="map-card-title">
                ${story.title}
              </div>

              <div class="map-card-description">
                ${story.short_description}
              </div>

              ${(story.related_pages || []).length ? `
                <div class="map-card-related">
                  ${relatedPages}
                </div>
              ` : ''}

              <div class="map-card-meta">
                <span>${story.publishing_date}</span>
                <span>${story.location}</span>
              </div>
            </div>
          `, {
            closeButton: false,
            autoClose: true,
            closeOnClick: false,
            autoPan: false,
            minWidth: popupWidth,
            maxWidth: popupWidth,
            offset: L.point(popupOffsetX, 0),
          });

          node.on('mouseover', () => {
            clearTimeout(closeTimeout);
            hub.closeTooltip();
            node.openPopup();
          });

          node.on('mouseout', () => {
            closeTimeout = setTimeout(collapseHub, 500);
          });

          node.on('popupopen', (event) => {
            const popup = event.popup.getElement();

            if (!popup) return;

            const mapHeight = map.getSize().y;
            const markerY = map.latLngToContainerPoint(node.getLatLng()).y;
            const popupHeight = popup.offsetHeight;
            const padding = 20;

            // Leaflet normally positions the popup above its marker.
            const spaceAbove = markerY - padding;
            const spaceBelow = mapHeight - markerY - padding;

            if (popupHeight > spaceAbove && spaceBelow > spaceAbove) {
              // Move the popup below the marker.
              event.popup.options.offset = L.point(popupOffsetX, popupHeight + 20);
            } else {
              // Keep it above, shifting downward if necessary.
              const overflow = Math.max(0, popupHeight - spaceAbove);
              event.popup.options.offset = L.point(popupOffsetX, overflow);
            }

            event.popup.update();

            popup.addEventListener('mouseenter', () => {
              clearTimeout(closeTimeout);
            });

            popup.addEventListener('mouseleave', () => {
              closeTimeout = setTimeout(collapseHub, 500);
            });
          });

          storyNodes.push(node);
        });
      };

      hub.on('mouseover', () => {
        expandHub();
        hub.openTooltip();
      });

      hub.on('mouseout', () => {
        closeTimeout = setTimeout(collapseHub, 500);
      });

      map.on('movestart', () => {
        clearTimeout(closeTimeout);
        collapseHub();
      });
    });

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, [slide]);

  return (
    <div className="annual-report-map">
      <div
        ref={mapContainerRef}
        className="annual-report-map-container"
      />
    </div>
  );
}

AnnualReportMap.propTypes = {
  slide: PropTypes.object.isRequired,
};

export default AnnualReportMap;
