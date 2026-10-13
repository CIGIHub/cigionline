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
      maxBounds: [
        [-85, -180],
        [85, 180],
      ],
      maxBoundsViscosity: 1.0,
    });

    const worldBounds = L.latLngBounds(
      [-60, -170],
      [85, 170]
    );

    const updateMapSize = () => {
      map.invalidateSize();

      // Remove the previous minimum zoom restriction
      map.setMinZoom(0);

      // Recalculate the zoom for the current container dimensions
      const minZoom = Math.min(
        map.getBoundsZoom(worldBounds, false, [20, 20]),
        1.5
      );

      map.setMinZoom(minZoom);

      // Zoom out if necessary, without resetting the user's position
      if (map.getZoom() < minZoom) {
        map.setZoom(minZoom);
      }
    };

    // Initial framing
    map.fitBounds(worldBounds, {
      padding: [20, 20],
      maxZoom: 1.5,
    });

    map.setMinZoom(map.getZoom());

    // Respond to container resizing
    const resizeObserver = new ResizeObserver(updateMapSize);
    resizeObserver.observe(mapContainerRef.current);

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

    fetch('/static/assets/ne_110m_admin_0_countries.geojson')
      .then((response) => {
        if (!response.ok) throw new Error('Failed to load country GeoJSON');
        return response.json();
      })
      .then((data) => {
        console.log(data.features[0].properties);
        L.geoJSON(data, {
          style: {
            className: 'map-country',
          },
          interactive: false,
        }).addTo(map);
      })
      .catch((error) => console.error(error));

    delete L.Icon.Default.prototype._getIconUrl;

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

      const expandHub = () => {
        clearTimeout(closeTimeout);

        if (storyNodes.length) return;

        const hubPoint = map.latLngToLayerPoint(hub.getLatLng());
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
          }).addTo(map);

          const popupWidth = Math.min(900, map.getSize().x - 40);
          const markerX = map.latLngToContainerPoint(node.getLatLng()).x;
          const mapWidth = map.getSize().x;

          // Shift the popup to stay within the map's horizontal boundaries
          const popupOffsetX = Math.max(
            popupWidth / 2 + 20 - markerX,
            Math.min(
              0,
              mapWidth - popupWidth / 2 - 20 - markerX
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

      hub.on('mouseover', () => {
        expandHub();
        hub.openTooltip();
      });hub.on('mouseover', expandHub);

      hub.on('mouseout', () => {
        closeTimeout = setTimeout(collapseHub, 500);
      });

      map.on('movestart', () => {
        clearTimeout(closeTimeout);
        collapseHub();
      });
    });

    if (markerBounds.length) {
      map.fitBounds(markerBounds, {
        padding: [40, 40],
        maxZoom: 5,
      });
    }

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
