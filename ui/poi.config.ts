import {
  Options
} from 'poi'

const options: Options = {
  entry: 'src/index.ts',
  staticFolder: './public',
  sourceMap: false,
  extractCSS: true,
  html: {
    template: 'index.html'
  },
  plugins: [require('@poi/plugin-typescript')()]
}

if (process.env.NODE_ENV === 'production') {
  options.filename = {
    js: 'static/js/[name].[chunkhash:8].js',
    css: 'static/css/[name].[chunkhash:8].css',
    image: 'static/img/[name].[ext]',
    font: 'static/fonts/[name].[ext]',
    chunk: 'static/js/[id].chunk.js'
  }
}

export default options
