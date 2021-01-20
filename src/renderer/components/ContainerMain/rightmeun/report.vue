<template>
  <div id="res_arr">
    <el-card style="margin: 15px">
      <el-container>
        <el-header><h4>移动图片</h4></el-header>
        <el-main class="receive-box">
          <el-form ref="form" :model="form" label-width="120px" style="width: 60%">
            <el-form-item label="搜索范围">
              <input type="file" id="search_range" hidden @change="searchFileRange" webkitdirectory>
              <el-input placeholder="搜索范围" v-model="form.searchFilePath" class="input-with-select">
                <el-button slot="append" icon="el-icon-folder" type="success" @click="onSearchRange"></el-button>
              </el-input>
            </el-form-item>

            <el-form-item label="原文件">
              <input type="file" id="move_file" accept="image/png, image/jpeg, image/jpg" multiple="multiple" hidden @change="maskFile">
              <el-input placeholder="移动的文件"  v-model="form.moveFileList" class="input-with-select">
                <el-button slot="append"  icon="el-icon-folder" type="success" @click="onMoveFile"></el-button>
              </el-input>
            </el-form-item>

            <el-form-item label="目标文件夹">
              <input type="file" id="target_file" hidden @change="fileChange" webkitdirectory>
              <el-input placeholder="目标文件夹" v-model="form.filePath" class="input-with-select">
                <el-button slot="append" icon="el-icon-folder" type="success" @click="onTargetFile"></el-button>
              </el-input>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="runMoveAllFile" plain>运行全部</el-button>
        </el-main>
      </el-container>
    </el-card>

      <el-card>
        <enhanced-table
            :tableData="tableData"
            :col-configs="colConfigs">
          <el-table-column slot="options" label="操作">
            <el-button size="mini" slot-scope="{ row }">查看</el-button>
          </el-table-column>
        </enhanced-table>
      </el-card>
  </div>
</template>
<script>
import EnhancedTable from '../../Table/EnhancedTable'

export default {
  name: 'res_arr',

  components: {
    EnhancedTable
  },

  data () {
    return {
      form: {
        moveFileList: [],
        filePath: '',
        searchFilePath: ''
      },
      colConfigs: [
        { prop: 'id', label: '序号' },
        { prop: 'move_file', label: '移动文件' },
        { prop: 'target_address', label: '目标地址' },
        { prop: 'status', label: '状态' },
        { slot: 'options', message: 'message' }
      ],
      tableData: []
    }
  },

  methods: {
    fileChange (e) {
      try {
        const fu = document.getElementById('target_file')
        if (fu == null) return
        const that = this
        let tbl = that.tableData
        let target = fu.files[0].path
        for (let i = 0; i < tbl.length; i++) {
          tbl[i].target_address = target
        }
        that.form.filePath = target
        that.tableData = tbl
        console.log('fileChange:', that.form.filePath)
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },

    maskFile () {
      try {
        const fileObj = document.getElementById('move_file')
        if (fileObj == null) return
        const that = this
        const files = fileObj.files
        that.form.moveFileList = files[0].path
        let tbl = that.tableData
        for (let i = 0; i < files.length; i++) {
          let file = files[i]
          tbl[tbl.length] = {
            id: tbl.length,
            move_file: file.path,
            target_address: that.form.filePath,
            status: '未运行'
          }
        }
        that.tableData = JSON.parse(JSON.stringify(tbl))
        console.log('mask file2', tbl)
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },

    searchFileRange () {
      try {
        const fileObj = document.getElementById('search_range')
        if (fileObj == null) return
        const that = this
        console.log('search file:', fileObj.files[0].path)
        that.form.searchFilePath = fileObj.files[0].path
        // that.setSearchRange()
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },

    clickFile (file) {
      file.click()
    },

    onMoveFile () {
      const file = document.getElementById('move_file')
      const that = this
      console.log('onclick file btn', file)
      that.clickFile(file)
    },

    onTargetFile () {
      const file = document.getElementById('target_file')
      const that = this
      that.clickFile(file)
    },

    onSearchRange () {
      const file = document.getElementById('search_range')
      const that = this
      that.clickFile(file)
    },

    getSearchRangeOrder () {
      const that = this
      const filePath = that.form.searchFilePath
      console.log('searchFilePath', filePath)
      if (filePath.length <= 0) {
        this.$message.error('未设置搜索范围')
        return
      }
      const pythonPath = '.\\src\\renderer\\plugins\\python\\res_arrange.py'
      const command = 'python ' + pythonPath + ' ' + filePath
      // that.testCmd(command)
      return command
    },

    runMoveAllFile: function () {
      const that = this
      const tbl = that.tableData
      let runOrder = ''
      let searchOrder = that.getSearchRangeOrder()
      for (let i = 0; i < tbl.length; i++) {
        let moveFile = tbl[i].move_file
        let targetPath = tbl[i].target_address
        let moveOrder = ' mv ' + moveFile + ' ' + targetPath
        runOrder = searchOrder + moveOrder
        console.log('-----run move------', runOrder)
        that.testCmd(runOrder)
      }
    },

    testCmd: function (command, id) {
      const that = this
      console.log('----- cmd order -----', command)
      that.$cmd.get(
        command,
        function (err, data, stderr) {
          console.log('----- cmd err -----', stderr)
          console.log('----- err mask -----', err)
          const h = that.$createElement;
          that.$notify({
            title: '提示',
            // eslint-disable-next-line standard/object-curly-even-spacing
            message: h('i', { style: 'color: teal'}, stderr)
          })
          if (!err) {
            that.$message({
              message: '运行成功',
              type: 'success'
            })
            console.log('the node-cmd log :', data)
          } else {
            console.log('error', err)
            this.$message.error('运行出错了')
          }
        }
      )
    }
  },
  mounted () {
  },
  destroyed () {
  }
}
</script>

<style scoped>
.receive-box {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: calc(100% - 230px);
}

.receive-windows {
  width: 100%;
  height: calc(100% - 26px);
  padding: 15px;
  overflow-y: scroll;
  overflow-x: hidden;
}

.send-header {
  height: 40px;
  padding-left: 15px;
  line-height: 26px;
  background-color: #FAFAFA;
  /*margin-bottom: 0;*/
}
</style>
