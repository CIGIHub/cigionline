import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../../../css/components/annual_reports/AnnualReportMap.scss';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

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

    const map = L.map(mapContainerRef.current).setView([20, 0], 2);
    map.attributionControl.setPrefix(false);
    mapRef.current = map;

    requestAnimationFrame(() => {
      map.invalidateSize();
    });

    const ReferrerTileLayer = L.TileLayer.extend({
      createTile(coords, done) {
        const tile = document.createElement('img');

        tile.referrerPolicy = 'strict-origin-when-cross-origin';

        L.DomEvent.on(tile, 'load', L.Util.bind(this._tileOnLoad, this, done, tile));
        L.DomEvent.on(tile, 'error', L.Util.bind(this._tileOnError, this, done, tile));

        tile.alt = '';
        tile.src = this.getTileUrl(coords);

        return tile;
      },
    });

    new ReferrerTileLayer(
      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
      },
    ).addTo(map);

    delete L.Icon.Default.prototype._getIconUrl;

    L.Icon.Default.mergeOptions({
      iconRetinaUrl: markerIcon2x,
      iconUrl: markerIcon,
      shadowUrl: markerShadow,
    });

    const markerBounds = [];

    Object.entries(countryGroups).forEach(([country, group]) => {
      const coordinates = countries[country];

      if (!coordinates) return;

      const hubPosition = [coordinates.latitude, coordinates.longitude];
      markerBounds.push(hubPosition);

      const hubIcon = L.divIcon({
        className: 'map-country-hub',
        html: `<div class="map-country-hub-circle">${group.stories.length}</div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      });

      const hub = L.marker(hubPosition, {
        icon: hubIcon,
      }).addTo(map);

      const storyNodes = [];
      let closeTimeout;

      const expandHub = () => {
        clearTimeout(closeTimeout);

        if (storyNodes.length) return;

        const hubPoint = map.latLngToLayerPoint(hub.getLatLng());
        const radius = 90;
        const count = group.stories.length;

        group.stories.forEach((story, index) => {
          const angle = -Math.PI / 2 + (Math.PI * index) / Math.max(count - 1, 1);

          const x = hubPoint.x + radius * Math.cos(angle);
          const y = hubPoint.y + radius * Math.sin(angle);

          const position = map.layerPointToLatLng([x, y]);

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
          })
            .addTo(map)
            .bindPopup(`
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
              autoClose: false,
              closeOnClick: false,
            });

          node.on('mouseover', () => {
            clearTimeout(closeTimeout);
            node.openPopup();
          });

          node.on('mouseout', () => {
            closeTimeout = setTimeout(collapseHub, 500);
          });

          node.on('popupopen', (event) => {
            const popup = event.popup.getElement();

            if (!popup) return;

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

      const collapseHub = () => {
        storyNodes.forEach((node) => {
          node.closePopup();
          map.removeLayer(node);
        });

        storyNodes.length = 0;
      };

      hub.on('mouseover', expandHub);

      hub.on('mouseout', () => {
        closeTimeout = setTimeout(collapseHub, 500);
      });
    });

    if (markerBounds.length) {
      map.fitBounds(markerBounds, {
        padding: [40, 40],
        maxZoom: 5,
      });
    }

    return () => {
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
