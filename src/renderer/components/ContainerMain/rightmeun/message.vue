<template>
  <div>
    <div id="dropbox" class="drop">
      <file-module></file-module>
    </div>
  </div>
</template>
<script>
import orderM from '@/components/ContainerMain/rightmeun/message/order'
import sendM from './message/send'
import fileModule from '../../files/file_module'

export default {
  components: {
    't-a': orderM,
    't-b': sendM,
    fileModule
  },
  data () {
    return {
      item1: true,
      item2: false,
      view: 't-a',
      flag: true,
      postObj: null,
      value: '',
      postFlag: false,
      filePath: ''
    }
  },
  methods: {
    chikcs1: function () {
      this.item1 = true
      this.item2 = false
      this.view = 't-a'
      // this.flag = false
    },
    chikcs2: function () {
      this.item1 = false
      this.item2 = true
      this.view = 't-b'
      // this.flag = true
    },
    onDrag (e) {
      e.stopPropagation()
      e.preventDefault()
    },
    onDrop (e) {
      e.stopPropagation()
      e.preventDefault()
      print('-----files-----', e.dataTransfer.files)
      this.files = e.dataTransfer.files
    }
  },
  // eslint-disable-next-line no-dupe-keys
  mounted () {
    const that = this
    that.$bus.$emit('getData')
    that.$bus.$on('postData', (data) => {
      that.postFlag = data.flag
      that.portObj = data.portObj
      that.value = data.comName
    })
    let upload = document.querySelector('.drop')
    upload.addEventListener('dragenter', this.onDrag, false)
    upload.addEventListener('dragover', this.onDrag, false)
    upload.addEventListener('drop', this.onDrop, false)
  },
  destroyed () {
    this.$bus.$off('postData')
  }
}
</script>
<style scoped>
.message-header {
  height: 40px;
  line-height: 40px;
  width: 100%;
  border-bottom: 1px solid #f1f1f1;
}

.message-header-tab {
  width: 60%;
  margin: 0 auto;
  display: flex;
  display: -webkit-flex;
  /* for uc */
  display: -webkit-box;
  display: -ms-flexbox;
}

.header-tab-item {
  -ms-flex: 1; /* IE 10 */
  -webkit-flex: 1;
  flex: 1;
  /* for uc */
  -webkit-box-flex: 1;
  -moz-box-flex: 1;
  text-align: center;
  cursor: pointer;
}

.message-main {
  width: 100%;
}

.active {
  border-bottom: 2px solid #27408B;
  color: #27408B;
}
</style>
