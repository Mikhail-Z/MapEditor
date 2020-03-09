var webpack = require("webpack")
var path = require("path")

process.noDeprecation = true

const NODE_ENV = process.env.NODE_ENV || "development"; 

module.exports = {
  entry: "./src/index.js",
  output: {
      path: path.join(__dirname, 'dist', 'assets'),
      filename: "bundle.js",
      sourceMapFilename: 'bundle.map'
  },
  mode: 'development',
  watchOptions: {
      aggregateTimeout: 100
  },
  devtool: '#source-map',
  module: {
    rules: [
        {
            test: /\.js$/,
            exclude: /(node_modules)/,
            loader: 'babel-loader',
            query: {
                presets: ['@babel/env', '@babel/react']
            }
        },
        {
            test: /\.css$/,
            use: ['style-loader','css-loader', {
                loader: 'postcss-loader',
                options: {
                  plugins: () => [require('autoprefixer')]
                }}]
        },
        {
            test: /\.scss/,
            use: ['style-loader','css-loader', {
                loader: 'postcss-loader',
                options: {
                  plugins: () => [require('autoprefixer')]
                }}, 'sass-loader']
        }
    ]
  }
}
