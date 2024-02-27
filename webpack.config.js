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
    filename: '[name].[contenthash].css',
  }),
];

const config = {
  context: __dirname,

  entry: {
    annualReportPage: './cigionline/static/pages/annual_report_page/index.js',
    annualReportListPage: './cigionline/static/pages/annual_report_list_page/index.js',
    articleLandingPage: './cigionline/static/pages/article_landing_page/index.js',
    articlePage: './cigionline/static/pages/article_page/index.js',
    articleSeriesPage: './cigionline/static/pages/article_series_page/index.js',
    articleSeriesListPage: './cigionline/static/pages/article_series_list_page/index.js',
    articleTypePage: './cigionline/static/pages/article_type_page/index.js',
    cigionline: './cigionline/static/index.js',
    eventListPage: './cigionline/static/pages/event_list_page/index.js',
    eventPage: './cigionline/static/pages/event_page/index.js',
    fundingPage: './cigionline/static/pages/funding_page/index.js',
    homePage: './cigionline/static/pages/home_page/index.js',
    igcTimelinePage: './cigionline/static/pages/igc_timeline_page/index.js',
    jobPostingListPage: './cigionline/static/pages/job_posting_list_page/index.js',
    jobPostingPage: './cigionline/static/pages/job_posting_page/index.js',
    mediaLandingPage: './cigionline/static/pages/media_landing_page/index.js',
    multimediaListPage: './cigionline/static/pages/multimedia_list_page/index.js',
    multimediaPage: './cigionline/static/pages/multimedia_page/index.js',
    multimediaSeriesPage: './cigionline/static/pages/multimedia_series_page/index.js',
    newsletterPage: './cigionline/static/pages/newsletter_page/index.js',
    personListExpertsPage: './cigionline/static/pages/person_list_experts_page/index.js',
    personListStaffPage: './cigionline/static/pages/person_list_staff_page/index.js',
    personPage: './cigionline/static/pages/person_page/index.js',
    projectPage: './cigionline/static/pages/project_page/index.js',
    publicationListPage: './cigionline/static/pages/publication_list_page/index.js',
    publicationPage: './cigionline/static/pages/publication_page/index.js',
    publicationSeriesPage: './cigionline/static/pages/publication_series_page/index.js',
    publicationTypePage: './cigionline/static/pages/publication_type_page/index.js',
    searchPage: './cigionline/static/pages/search_page/index.js',
    researchLandingPage: './cigionline/static/pages/research_landing_page/index.js',
    subscribePage: './cigionline/static/pages/subscribe_page/index.js',
    themeAccents: './cigionline/static/themes/accents/index.js',
    themeAfterCovidSeries: './cigionline/static/themes/after_covid_series/index.js',
    themeAIEthicsSeries: './cigionline/static/themes/ai_ethics_series/index.js',
    themeAISeries: './cigionline/static/themes/ai_series/index.js',
    themeBigTech: './cigionline/static/themes/big_tech/index.js',
    themeBigTechS3: './cigionline/static/themes/big_tech_s3/index.js',
    themeCyberSeries: './cigionline/static/themes/cyber_series/index.js',
    themeDataSeries: './cigionline/static/themes/data_series/index.js',
    themeDPH: './cigionline/static/themes/dph/index.js',
    themeFreedomOfThought: './cigionline/static/themes/freedom_of_thought/index.js',
    themeFourDomainsSeries: './cigionline/static/themes/four_domains_series/index.js',
    themeGES: './cigionline/static/themes/ges/index.js',
    themeHealthSecuritySeries: './cigionline/static/themes/health_security_series/index.js',
    themeIgc: './cigionline/static/themes/igc/index.js',
    themeIndigenousLandsSeries: './cigionline/static/themes/indigenous_lands_series/index.js',
    themeInnovationSeries: './cigionline/static/themes/innovation_series/index.js',
    themeJohnHolmesSeries: './cigionline/static/themes/john_holmes_series/index.js',
    themeLongform: './cigionline/static/themes/longform/index.js',
    themeLongform2: './cigionline/static/themes/longform_2/index.js',
    themeLongform2DarkMode: './cigionline/static/themes/longform_2_dark_mode/index.js',
    themeOGBV: './cigionline/static/themes/ogbv/index.js',
    themePfPCSeries: './cigionline/static/themes/pfpc_series/index.js',
    themePlatformGovernanceSeries: './cigionline/static/themes/platform_governance_series/index.js',
    themeSpaceSeries: './cigionline/static/themes/space_series/index.js',
    themeSpecialOpinions: './cigionline/static/themes/special_opinions/index.js',
    themeWomenAndTradeSeries: './cigionline/static/themes/women_and_trade_series/index.js',
    themeWTOSeries: './cigionline/static/themes/wto_series/index.js',
    topicPage: './cigionline/static/pages/topic_page/index.js',
    twentiethPage: './cigionline/static/pages/twentieth_page/index.js',
    twentiethPageSingleton: './cigionline/static/pages/twentieth_page_singleton/index.js',
  },

  devtool: 'source-map',
  output: {
    path: path.resolve('./cigionline/static/bundles/'),
    publicPath: '/static/bundles/',
    filename: '[name].[contenthash].js',
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
