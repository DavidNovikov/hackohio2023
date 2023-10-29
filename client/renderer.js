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

window.versions.onPythonChildPort((event, port) => {
  console.log(`Python child process listening on port ${port}`)
  const socket = new WebSocket(`ws://localhost:${port}`)
  socket.addEventListener('open', () => {
    console.log('WebSocket connection opened')
    socket.send('Hello from client')
  })
  socket.addEventListener('message', (event) => {
    console.log('WebSocket message received:', event.data)
  })
})