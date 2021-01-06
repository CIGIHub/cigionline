const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const plugins = [
  new webpack.DefinePlugin({
    __DEV__: process.env.NODE_ENV === 'development',
    __PROD__: process.env.NODE_ENV === 'production',
  }),
  new webpack.ProvidePlugin({
    $: 'jquery',
    jQuery: 'jquery',
    'window.jQuery': 'jquery',
  }),
  new BundleTracker({ filename: './webpack-stats.json' }),
  new MiniCssExtractPlugin({
    filename: '[name].css',
  }),
];

const config = {
  context: __dirname,

  entry: {
    articleLandingPage: './cigionline/static/pages/article_landing_page/index.js',
    articlePage: './cigionline/static/pages/article_page/index.js',
    cigionline: './cigionline/static/index.js',
    eventListPage: './cigionline/static/pages/event_list_page/index.js',
    eventPage: './cigionline/static/pages/event_page/index.js',
    multimediaListPage: './cigionline/static/pages/multimedia_list_page/index.js',
    multimediaPage: './cigionline/static/pages/multimedia_page/index.js',
    publicationListPage: './cigionline/static/pages/publication_list_page/index.js',
    publicationPage: './cigionline/static/pages/publication_page/index.js',
    themeAfterCovidSeries: './cigionline/static/themes/after_covid_series/index.js',
    themeAISeries: './cigionline/static/themes/ai_series/index.js',
    themeBigTechS3: './cigionline/static/themes/big_tech_s3/index.js',
    themeDataSeries: './cigionline/static/themes/data_series/index.js',
    themeInnovationSeries: './cigionline/static/themes/innovation_series/index.js',
    themeLongform: './cigionline/static/themes/longform/index.js',
  },

  devtool: 'source-map',
  output: {
    path: path.resolve('./cigionline/static/bundles/'),
    publicPath: '/static/bundles/',
    filename: '[name].js',
  },
  plugins,

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: [/node_modules/, /vendor/],
        use: ['babel-loader?cacheDirectory=true', 'source-map-loader'],
      },
      {
        test: /\.scss$/,
        use: [
          { loader: MiniCssExtractPlugin.loader, options: { publicPath: '' } },
          { loader: 'css-loader', options: { sourceMap: true } },
          { loader: 'postcss-loader', options: { sourceMap: true } },
          { loader: 'resolve-url-loader', options: { sourceMap: true } },
          { loader: 'sass-loader', options: { sourceMap: true } },
        ],
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          { loader: 'css-loader', options: { importLoaders: 1 } },
          {
            loader: 'postcss-loader',
          },
        ],
      },
      {
        test: /\.(gif|jpe|jpg|png|jpeg|woff|woff2|eot|ttf)(\?.*$|$)/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name() {
                return '[name]-[hash].[ext]';
              },
            },
          },
          {
            loader: 'image-webpack-loader',
            options: {
              bypassOnDebug: true,
              pngquant: {
                enabled: false,
              },
            },
          },
        ],
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name() {
                return '[name]-[hash].[ext]';
              },
            },
          },
        ],
      },
    ],
  },
  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx', '.scss'],
    alias: {
    },
  },
};

module.exports = config;
