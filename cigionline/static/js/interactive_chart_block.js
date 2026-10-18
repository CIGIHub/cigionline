import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(ChartDataLabels);

const COLORS = [
  '#e02f2f',
  '#1d6fa5',
  '#e29e20',
  '#27856f',
  '#754668',
  '#6b6b6b',
  '#8b5a2b',
  '#4f7c23',
  '#724bc4',
  '#007f8b',
];

const withAlpha = (hex, alpha) => `${hex}${alpha}`;

const initializeChart = (element) => {
  const canvas = element.querySelector('canvas');
  const configElement = document.getElementById(element.dataset.chartConfigId);
  if (!canvas || !configElement) return;

  const config = JSON.parse(configElement.textContent);
  const circular = ['pie', 'doughnut'].includes(config.type);
  const horizontal = config.type === 'horizontal_bar';
  const line = ['line', 'area'].includes(config.type);
  const area = config.type === 'area';
  const numberFormatter = new Intl.NumberFormat(document.documentElement.lang || 'en');

  if (horizontal) {
    element.querySelector('.interactive-chart-canvas').style.height =
      `${Math.max(420, config.labels.length * 44)}px`;
  }

  config.datasets.forEach((dataset, index) => {
    if (circular) {
      dataset.backgroundColor = config.labels.map(
        (_, colorIndex) => COLORS[colorIndex % COLORS.length],
      );
      dataset.hoverOffset = 12;
      dataset.borderColor = '#fff';
    } else {
      const color = COLORS[index % COLORS.length];
      dataset.backgroundColor = withAlpha(color, area ? '55' : 'cc');
      dataset.borderColor = color;
      dataset.borderWidth = line ? 3 : 2;
      dataset.fill = area;
      dataset.pointBackgroundColor = color;
      dataset.pointHitRadius = line ? 12 : 1;
      dataset.pointRadius = line ? 0 : 4;
      dataset.pointHoverRadius = line ? 6 : 7;
      dataset.showLine = line;
      dataset.hoverBackgroundColor = color;
    }
  });

  new Chart(canvas, {
    type: line ? 'line' : horizontal ? 'bar' : config.type,
    data: {
      labels: config.labels,
      datasets: config.datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: horizontal ? 'y' : 'x',
      interaction: {
        intersect: !line,
        mode: 'nearest',
      },
      layout: {
        padding: 24,
      },
      plugins: {
        datalabels: {
          align: circular ? 'center' : 'end',
          anchor: circular ? 'center' : 'end',
          color: circular ? '#fff' : '#222',
          display: (context) => !line && context.dataset.data[context.dataIndex] !== null,
          font: {
            weight: 600,
          },
          formatter: (value) => numberFormatter.format(value),
        },
        legend: {
          display: line || config.datasets.length > 1 || circular,
          position: 'bottom',
        },
        tooltip: {
          enabled: true,
        },
      },
      scales: circular
        ? {}
        : {
            x: {
              grid: {
                display: horizontal,
              },
            },
            y: {
              beginAtZero: ['bar', 'horizontal_bar'].includes(config.type),
              grid: {
                display: !horizontal,
              },
            },
          },
    },
  });
};

export default function initializeInteractiveCharts() {
  document.querySelectorAll('.interactive-chart').forEach(initializeChart);
}
