const func = async () => {
  const response = await window.versions.ping()
  console.log(response) // prints out 'pong'
}

func()

Split(['#item-gallery', '#menu'], {
  minSize: 300,
  sizes: [75, 25],
})

const items = document.querySelectorAll('.item')

for (const item of items) {
  item.addEventListener('click', () => {
    if (item.classList.contains('selected')) {
      item.classList.remove('selected')
    } else {
      document.querySelector('.item.selected')?.classList.remove('selected')
      item.classList.add('selected')
    }
  })
}

let socket = null
window.versions.onPythonChildPort((event, port) => {
  console.log(`Python child process listening on port ${port}`)
  socket = new WebSocket(`ws://localhost:${port}`)
  socket.addEventListener('open', () => {
    console.log('WebSocket connection opened')
  })
  socket.addEventListener('message', (event) => {
    console.log('WebSocket message received:', event.data)
  })
})

function send(command, data={}) {
  if (socket) {
    const json = {
      command: command,
      data: data,
    }
    socket.send(JSON.stringify(json))
  } else {
    console.error('WebSocket connection not opened')
  }
}

const buttonBegin = document.getElementById('button-begin')
const buttonStop = document.getElementById('button-stop')

buttonBegin.addEventListener('click', () => {
  buttonBegin.disabled = true
  buttonStop.disabled = false
  buttonBegin.classList.add('disabled')
  buttonStop.classList.remove('disabled')

  send('beginProcedure')
})

buttonStop.addEventListener('click', () => {
  buttonBegin.disabled = false
  buttonStop.disabled = true
  buttonBegin.classList.remove('disabled')
  buttonStop.classList.add('disabled')

  send('stopProcedure')
})
