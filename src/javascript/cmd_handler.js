var nodeCmd = require('node-cmd')

// eslint-disable-next-line no-unused-vars
function runCmdGet (command) {
  nodeCmd.get(
    command,
    // eslint-disable-next-line handle-callback-err
    function (err, data, stderr) {
      console.log(data)
    }
  )
}

// eslint-disable-next-line no-unused-vars
function runCmdRun (command) {
  nodeCmd.run(command)
}
