<template>
  <el-card style="margin: 15px">
    <el-container>
      <el-header><h4>移动图片</h4></el-header>
      <el-main class="receive-box">
        <el-form ref="form" :model="form" label-width="120px" style="width: 60%">
          <el-form-item label="原文件">
            <input type="file" id="move_file" hidden @change="maskFile" webkitdirectory>
            <el-input placeholder="移动的文件" v-model="moveFileList" class="input-with-select">
              <el-button slot="append" icon="el-icon-folder" type="success" @click="btnChange"></el-button>
            </el-input>
          </el-form-item>
        </el-form>

        <el-form ref="form" :model="form" label-width="120px" style="width: 60%">
          <el-form-item label="目标文件夹">
            <input type="file" id="target_file" hidden @change="fileChange" webkitdirectory>
            <el-input placeholder="目标文件夹" v-model="filePath" class="input-with-select">
              <el-button slot="append" icon="el-icon-folder" type="success" @click="btnChange"></el-button>
            </el-input>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="testCmd" plain>运行</el-button>
      </el-main>
    </el-container>
  </el-card>

<!--  <div>-->
<!--    <el-card>-->
<!--      <enhanced-table-->
<!--          :tableData="tableData"-->
<!--          :col-configs="colConfigs">-->
<!--        <el-table-column slot="options" label="操作">-->
<!--          <el-button size="mini" slot-scope="{ row }">查看</el-button>-->
<!--        </el-table-column>-->
<!--      </enhanced-table>-->
<!--    </el-card>-->
<!--  </div>-->
</template>

<script>
import EnhancedTable from '../../Table/EnhancedTable'

export default {
  name: 'send',

  components: {
    EnhancedTable
  },

  data () {
    return {
      moveFileList: {},
      filePath: '',
      colConfigs: [
        { prop: 'id', label: '序号' },
        { prop: 'more_file', label: '移动文件' },
        { prop: 'target_address', label: '目标地址' },
        { slot: 'options', message: 'message' }
      ],
      tableData: [{
        id: '1',
        more_file: '2016-05-02',
        target_address: '王小虎'
      }, {
        id: '2',
        more_file: '2016-05-04',
        target_address: '王小虎'
      }]
    }
  },

  methods: {
    fileChange (e) {
      try {
        const fu = document.getElementById('file')
        if (fu == null) return
        const that = this
        that.filePath = fu.files[0].path
        console.log('fileChange:', that.filePath)
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },

    maskFile () {
      try {
        const fileObj = document.getElementById('file')
        if (fileObj == null) return
        const that = this
        that.moveFileList = fileObj.files
        console.log('mask file:', fileObj.files)
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },

    btnChange () {
      const file = document.getElementById('file')
      file.click()
    },

    testCmd: function () {
      const that = this
      const filePath = that.form.filePath
      console.log('file path', filePath)
      const pythonPath = '.\\src\\renderer\\plugins\\python\\res_arrange.py'
      const command = 'python ' + pythonPath + ' ' + filePath
      that.$cmd.get(
        command,
        function (err, data, stderr) {
          console.log(stderr)
          if (!err) {
            that.$message({
              message: '运行成功',
              type: 'success'
            })
            console.log('the node-cmd cloned dir contains these files :', data)
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
