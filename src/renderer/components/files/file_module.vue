<template>

  <el-container>
    <el-header><h4>生成complex</h4></el-header>

    <el-main class="bodyTip">
      <el-form ref="form" :model="form" label-width="120px" style="width: 60%">
        <el-form-item label="目标文件夹">
          <input type="file" id="file" hidden @change="fileChange" webkitdirectory>
          <el-input placeholder="请输入内容" v-model="form.filePath" class="input-with-select">
            <el-button slot="append" icon="el-icon-folder" type="success" @click="btnChange"></el-button>
          </el-input>
          <el-button type="primary" @click="testCmd" plain>运行</el-button>
        </el-form-item>
      </el-form>
    </el-main>
  </el-container>

</template>

<script>
export default {
  name: 'file_module',
  data () {
    return {
      form: {
        filePath: ''
      }
    }
  },
  methods: {
    fileChange (e) {
      try {
        const fu = document.getElementById('file')
        if (fu == null) return
        const that = this
        that.form.filePath = fu.files[0].path
        console.log('fileChange:', that.form.filePath)
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
      const pythonPath = '.\\src\\renderer\\plugins\\python\\gen_complex.py'
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
  }
}
</script>
<style scoped>

.bodyTip {
  display: flex;
  justify-content: space-between;
}

</style>