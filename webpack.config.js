const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

let plugins = [
    new webpack.DefinePlugin({
        __DEV__: process.env.NODE_ENV === 'development',
        __PROD__: process.env.NODE_ENV === 'production',
    }),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery',
        Popper: ['popper.js', 'default']
    }),
    new BundleTracker({filename: './webpack-stats.json'}),
]

const config = {
    context: __dirname,

    entry: {
        cigionlineJs: "./cigionline/static/js/cigionline.js",
        cigionlineCss: "./cigionline/static/css/cigionline.scss",
    },

    devtool: 'source-map',
    output: {
        path: path.resolve('./bundles/'),
        filename: '[name].js',
    },
    plugins: plugins,

    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: [/node_modules/, /vendor/],
                use: ['babel-loader?cacheDirectory=true', 'source-map-loader']
            },
            {
                test: /\.scss$/,
                use: [
                    // Creates `style` nodes from JS strings
                    'style-loader',
                    // Translates CSS into CommonJS
                    'css-loader',
                    // Compiles Sass to CSS
                    'sass-loader',
                ]

            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    {loader: 'css-loader', options: {importLoaders: 1}},
                    {
                        loader: 'postcss-loader'
                    }
                ]
            },
            {
                test: /\.(gif|jpe|jpg|png|jpeg|woff|woff2|eot|ttf)(\?.*$|$)/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name(file) {
                                if (process.env.NODE_ENV === 'development') {
                                    return '[name]-[hash].[ext]';
                                }

                                return '[name]-[hash].[ext]';
                            },
                        },
                    },
                    {
                        loader: 'image-webpack-loader',
                        options: {
                            bypassOnDebug: true,
                            pngquant: {
                                enabled: false
                            },
                        }
                    },
                ]
            },
            {
                test: /\.svg$/,
                issuer: {
                    test: /\.js?$/
                },
                use: ['@svgr/webpack', 'url-loader'],
            },
            {
                test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                loader: 'url-loader'
            },
        ]
    },
    resolve: {
        modules: ['node_modules'],
        extensions: ['.js', '.jsx', '.scss'],
        alias: {
        }
    }
};

module.exports = config;
