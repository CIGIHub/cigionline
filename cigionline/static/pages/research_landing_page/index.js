import React from 'react';
import ReactDOM from 'react-dom';
import * as d3 from 'd3';
import ResearchContentListing from '../../js/components/ResearchContentListing';
import SearchTable from '../../js/components/SearchTable';
import './css/research_landing_page.scss';

function drawTreeMap() {
  // set the dimensions and margins of the graph
  const margin = { top: 10, right: 0, bottom: 10, left: 0 };
  const width = 1280 - margin.left - margin.right;
  const height = 640 - margin.top - margin.bottom;

  // append the svg object to the body of the page
  const svg = d3
    .select('#topics-container')
    .append('svg')
    .attr('width', '100%')
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`);

  const topics = document
    .getElementById('topics-container')
    .dataset.tree.replace(/'/g, '"');
  const data = JSON.parse(topics);

  // Give the data to this cluster layout:
  const root = d3
    .hierarchy(data)
    .sum(function (d) {
      return d.value;
    })
    .sort(function (a, b) {
      return b.value - a.value;
    });

  // Then d3.treemap computes the position of each element of the hierarchy
  d3.treemap().size([width, height]).padding(2)(root);

  const tooltip = svg
    .append('div')
    .style('position', 'absolute')
    .style('z-index', '10')
    .style('visibility', 'hidden')
    .style('background-color', 'white')
    .style('border', 'solid')
    .style('border-width', '2px')
    .style('border-radius', '5px')
    .style('padding', '5px');

  // use this information to add rectangles:
  const rects = svg
    .selectAll('rect')
    .data(root.leaves())
    .join('rect')
    .attr('x', function (d) {
      return d.x0;
    })
    .attr('y', function (d) {
      return d.y0;
    })
    .attr('width', function (d) {
      return d.x1 - d.x0;
    })
    .attr('height', function (d) {
      return d.y1 - d.y0;
    })
    .attr('rx', '15')
    .style('padding', '10px')
    .style('fill', '#f6f6f6')
    .on('mouseover', function (d, i) {
      let text;
      texts.each(function (c, i2) {
        if (c === i) {
          text = d3.select(this);
        }
      });
      text.attr('fill', '#f6f6f6');
    })
    .on('mouseout', function (d, i) {
      let text;
      texts.each(function (c, i2) {
        if (c === i) {
          text = d3.select(this);
        }
      });
      text.attr('fill', 'black');
    });

  // and to add the text labels
  const texts = svg
    .selectAll('text')
    .data(root.leaves())
    .join('text')
    .attr('x', function (d) {
      return d.x0 + 15;
    })
    .attr('y', function (d) {
      const area = (d.x1 - d.x0) * (d.y1 - d.y0);
      const fontSize = Math.sqrt(area / 100) < 12 ? 12 : Math.sqrt(area / 100);
      return d.y0 + fontSize * 1.5;
    })
    .text(function (d) {
      return d.data.name;
    })
    .attr('font-size', function (d) {
      const area = (d.x1 - d.x0) * (d.y1 - d.y0);
      const fontSize = Math.sqrt(area / 100) < 12 ? 12 : Math.sqrt(area / 100);
      return `${fontSize}px`;
    })
    .attr('class', 'topic-label')
    .attr('fill', 'black');

  const vals = svg
    .selectAll('vals')
    .data(root.leaves())
    .enter()
    .append('text')
    .attr('x', function (d) {
      return d.x0 + 15;
    })
    .attr('y', function (d) {
      const area = (d.x1 - d.x0) * (d.y1 - d.y0);
      const fontSize = Math.sqrt(area / 100) < 12 ? 12 : Math.sqrt(area / 100);
      return d.y0 + fontSize * 1.5 + 20;
    })
    .text(function (d) {
      return `(${d.data.value})`;
    })
    .attr('font-size', '11px')
    .attr('fill', '#6d6d6d');
}

drawTreeMap();

ReactDOM.render(
  <SearchTable
    showSearch
    contenttypes={['Publication', 'Opinion', 'Event', 'Multimedia', 'Activity']}
    fields={[
      'authors',
      'contentsubtype',
      'contenttype',
      'pdf_download',
      'publishing_date',
      'topics',
    ]}
    containerClass={['custom-theme-table']}
    filterTypes={[
      {
        name: 'Event',
        params: [
          {
            name: 'contenttype',
            value: 'Event',
          },
        ],
      },
      {
        name: 'Publication',
        params: [
          {
            name: 'contenttype',
            value: 'Publication',
          },
        ],
      },
      {
        name: 'Multimedia',
        params: [
          {
            name: 'contenttype',
            value: 'Multimedia',
          },
        ],
      },
      {
        name: 'Opinion',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Opinion',
          },
        ],
      },
      {
        name: 'Op-Eds',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'Op-Eds',
          },
        ],
      },
      {
        name: 'CIGI in the News',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'CIGI in the News',
          },
        ],
      },
      {
        name: 'News Releases',
        aggregationField: 'contentsubtypes',
        params: [
          {
            name: 'contentsubtype',
            value: 'News Releases',
          },
        ],
      },
      {
        name: 'Research Project',
        alias: 'research.ProjectPage',
        aggregationField: 'content_types',
        params: [
          {
            name: 'content_type',
            value: 'research.ProjectPage',
          },
        ],
      },
    ]}
    RowComponent={ResearchContentListing}
    tableColumns={[
      {
        colSpan: 4,
        colTitle: 'Title',
      },
      {
        colSpan: 3,
        colTitle: 'Expert',
      },
      {
        colSpan: 2,
        colTitle: 'Topic',
      },
      {
        colSpan: 2,
        colTitle: 'Type',
      },
      {
        colSpan: 1,
        colTitle: 'PDF',
      },
    ]}
  />,
  document.getElementById('research-search-table')
);
