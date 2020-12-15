const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const plugins = [
  new webpack.DefinePlugin({
    __DEV__: process.env.NODE_ENV === 'development',
    __PROD__: process.env.NODE_ENV === 'production',
  }),
  new webpack.ProvidePlugin({
    $: 'jquery',
    jQuery: 'jquery',
    'window.jQuery': 'jquery',
    Popper: ['popper.js', 'default'],
  }),
  new BundleTracker({ filename: './webpack-stats.json' }),
  new ExtractTextPlugin({
    filename: '[name].css',
    allChunks: true,
  }),
];

const config = {
  context: __dirname,

  entry: {
    cigionline: './cigionline/static/index.js',
    multimediaListPage: './cigionline/static/multimedia_list_page.js',
    multimediaPage: './cigionline/static/pages/multimedia_page/index.js',
    publicationListPage: './cigionline/static/publication_list_page.js',
    publicationPage: './cigionline/static/pages/publication_page/index.js',
    themeLongform: './cigionline/static/themes/longform/index.js',
  },

  devtool: 'source-map',
  output: {
    path: path.resolve('./cigionline/static/bundles/'),
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
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [
            { loader: 'css-loader', options: { sourceMap: true } },
            { loader: 'postcss-loader', options: { sourceMap: 'inline' } },
            { loader: 'resolve-url-loader', options: { sourceMap: true } },
            { loader: 'sass-loader', options: { sourceMap: true } },
          ],
        }),
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
        test: /\.svg$/,
        issuer: {
          test: /\.js?$/,
        },
        use: ['@svgr/webpack', 'url-loader'],
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
