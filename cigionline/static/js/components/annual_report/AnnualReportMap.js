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

    const map = L.map(mapContainerRef.current).setView([20, 0], 2);
    map.attributionControl.setPrefix(false);
    mapRef.current = map;

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

    stories.forEach((page) => {
      markerBounds.push([page.latitude, page.longitude]);

      const relatedPages = (page.related_pages || [])
        .map((related) => `
          <a href="${related.url}">
            ${related.title}
          </a>
        `)
        .join('');

      const marker = L.marker([page.latitude, page.longitude])
        .addTo(map)
        .bindPopup(`
          <div class="map-card">
            <div class="map-card-title">
              ${page.title}
            </div>

            ${page.research_theme ? `
              <div class="map-card-theme">
                ${page.research_theme}
              </div>
            ` : ''}

            <div class="map-card-description">
              ${page.short_description}
            </div>

            ${(page.related_pages || []).length ? `
              <div class="map-card-related">
                ${relatedPages}
              </div>
            ` : ''}

            <div class="map-card-meta">
              <span>${page.publishing_date}</span>
              <span>${page.location}</span>
            </div>
          </div>
        `, {
          closeButton: false,
          autoClose: false,
          closeOnClick: false,
        });

      let closeTimeout;

      marker.on('mouseover', () => {
        clearTimeout(closeTimeout);
        marker.openPopup();

        const popup = marker.getPopup().getElement();

        if (!popup) return;

        popup.addEventListener('mouseenter', () => {
          clearTimeout(closeTimeout);
        });

        popup.addEventListener('mouseleave', () => {
          marker.closePopup();
        });
      });

      marker.on('mouseout', () => {
        closeTimeout = setTimeout(() => {
          marker.closePopup();
        }, 500);
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
