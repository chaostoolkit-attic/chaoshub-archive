import Vue from 'vue'
import App from './App.vue'
import { createRouter } from './routes'
import './assets/sass/main.scss'

// tslint:disable-next-line:no-unused-expression
new Vue({
  el: '#app',
  router: createRouter(),
  render: h => h(App)
})
