const { app, BrowserWindow, ipcMain } = require('electron')
const child_process = require('child_process')
const path = require('node:path')

let win = null
const createWindow = () => {
  win = new BrowserWindow({
    width: 800,
    height: 600,
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

function startPythonChild() {
  const process = child_process.spawn('python', ['../python/server.py'])
  process.stdout.on('data', (data) => {
    console.log('Python child process stdout:', data.toString())
    let lines = data.toString().split('\n')
    lines = lines.filter(line => line.startsWith('>> '));
    lines = lines.map(line => line.substring(3))
    console.log('Parced commands:', lines)
    const port = parseInt(lines[0])
    win.webContents.send('pythonChildPort', port)
  })
  console.log('Python child process started')
}