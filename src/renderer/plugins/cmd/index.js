/**
 * 自定义cmd插件
 * @author LG32
 * @date 2021/1/15
 */
const cmdPlugin = {
  install (Vue) {
    Vue.prototype.$cmd = require('node-cmd')
  }
}

export default cmdPlugin
