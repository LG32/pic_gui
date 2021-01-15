import Vue from 'vue'
import axios from 'axios'
import App from './App'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import cmd from './plugins/cmd/index'

// import 'element-ui/lib/theme-chalk/index.css'
import '../style/element-style/theme/index.css'
Vue.use(ElementUI)
Vue.use(cmd)
if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.http = Vue.prototype.$http = axios
Vue.prototype.$bus = new Vue()
Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app')
