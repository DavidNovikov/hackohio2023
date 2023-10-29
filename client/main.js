const { app, BrowserWindow, ipcMain } = require('electron')
const child_process = require('child_process')
const path = require('node:path')

let win = null
const createWindow = () => {
  win = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.loadFile('index.html')
}

app.whenReady().then(() => {
  ipcMain.handle('ping', () => 'pong')
  createWindow()
  startPythonChild()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

let pythonChildPort = null
function startPythonChild() {
  const process = child_process.spawn('python', ['../python/server.py'])
  process.stderr.on('data', (data) => {
    console.error('Python child process stderr:', data.toString())
  })

  process.stdout.on('data', (data) => {
    console.log('Python child process stdout:', data.toString())
    let lines = data.toString().split('\n')
    lines = lines.filter(line => line.startsWith('>> '));
    lines = lines.map(line => line.substring(3))
    console.log('Parsed commands:', lines)
    if (!pythonChildPort && lines.length > 0) {
      pythonChildPort = parseInt(lines[0])
      win.webContents.send('pythonChildPort', pythonChildPort)
    }
  })
  console.log('Python child process started')
}