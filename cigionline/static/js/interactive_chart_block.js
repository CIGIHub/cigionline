import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(ChartDataLabels);

const COLORS = [
  '#E6023B',
  '#000000',
  '#747373',
  '#A4A4A4',
  '#DBDBDB',
  '#67BF8F',
  '#3F4F70',
  '#957AA9',
  '#D2B85E',
  '#D84D4C',
];
const COLORS_WITH_DARK_LABELS = new Set([
  '#A4A4A4',
  '#DBDBDB',
  '#67BF8F',
  '#957AA9',
  '#D2B85E',
  '#D84D4C',
]);

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
  const datasetStyles = [];

  if (horizontal) {
    element.querySelector('.interactive-chart-canvas').style.height =
      `${Math.max(420, config.labels.length * 44)}px`;
  }

  config.datasets.forEach((dataset, index) => {
    if (circular) {
      const backgroundColor = config.labels.map(
        (_, colorIndex) => COLORS[colorIndex % COLORS.length],
      );
      dataset.backgroundColor = backgroundColor;
      dataset.hoverOffset = 12;
      dataset.borderColor = '#fff';
      datasetStyles.push({
        backgroundColor,
        borderColor: config.labels.map(() => '#fff'),
        fadedBackgroundColor: backgroundColor.map((color) => withAlpha(color, '22')),
        fadedBorderColor: config.labels.map(() => '#ffffff33'),
      });
    } else {
      const color = COLORS[index % COLORS.length];
      const backgroundColor = withAlpha(color, area ? '55' : 'cc');
      dataset.backgroundColor = backgroundColor;
      dataset.borderColor = color;
      dataset.borderWidth = line ? 3 : 2;
      dataset.fill = area;
      dataset.pointBackgroundColor = color;
      dataset.pointHitRadius = line ? 12 : 1;
      dataset.pointRadius = line ? 0 : 4;
      dataset.pointHoverRadius = line ? 6 : 7;
      dataset.showLine = line;
      dataset.hoverBackgroundColor = color;
      datasetStyles.push({
        backgroundColor,
        borderColor: color,
        fadedBackgroundColor: withAlpha(color, '22'),
        fadedBorderColor: withAlpha(color, '33'),
      });
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
      onHover: (_, activeElements, chart) => {
        const focusedDatasetIndex = activeElements[0]?.datasetIndex ?? null;
        const focusedDataIndex = circular ? (activeElements[0]?.index ?? null) : null;
        if (
          chart.$focusedDatasetIndex === focusedDatasetIndex &&
          chart.$focusedDataIndex === focusedDataIndex
        )
          return;

        chart.$focusedDatasetIndex = focusedDatasetIndex;
        chart.$focusedDataIndex = focusedDataIndex;
        chart.data.datasets.forEach((dataset, index) => {
          const style = datasetStyles[index];
          if (circular) {
            dataset.backgroundColor = style.backgroundColor.map((color, dataIndex) =>
              focusedDatasetIndex === null ||
              (index === focusedDatasetIndex && dataIndex === focusedDataIndex)
                ? color
                : style.fadedBackgroundColor[dataIndex],
            );
            dataset.borderColor = style.borderColor.map((color, dataIndex) =>
              focusedDatasetIndex === null ||
              (index === focusedDatasetIndex && dataIndex === focusedDataIndex)
                ? color
                : style.fadedBorderColor[dataIndex],
            );
            return;
          }

          const faded = focusedDatasetIndex !== null && index !== focusedDatasetIndex;
          dataset.backgroundColor = faded ? style.fadedBackgroundColor : style.backgroundColor;
          dataset.borderColor = faded ? style.fadedBorderColor : style.borderColor;
        });
        chart.update('none');
      },
      layout: {
        padding: 24,
      },
      plugins: {
        datalabels: {
          align: circular ? 'center' : 'end',
          anchor: circular ? 'center' : 'end',
          color: (context) => {
            const focusedDatasetIndex = context.chart.$focusedDatasetIndex;
            const color =
              circular && COLORS_WITH_DARK_LABELS.has(COLORS[context.dataIndex % COLORS.length])
                ? '#000000'
                : circular
                  ? '#ffffff'
                  : '#222222';
            const faded =
              focusedDatasetIndex !== null &&
              focusedDatasetIndex !== undefined &&
              (context.datasetIndex !== focusedDatasetIndex ||
                (circular && context.dataIndex !== context.chart.$focusedDataIndex));
            return faded ? withAlpha(color, '33') : color;
          },
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
